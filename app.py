import streamlit as st
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from utils.helpers import load_data, generate_random_data, compute_metrics
from algorithms.first_fit import first_fit
from algorithms.best_fit import best_fit
from algorithms.min_min import min_min
from algorithms.max_min import max_min
from algorithms.genetic import genetic_algorithm
from models.entities import VM

# Configuration de la page
st.set_page_config(page_title="Cloud Scheduling Algorithms", layout="wide")
st.title("☁️ Comparaison d'algorithmes d'ordonnancement Cloud")

# Sidebar pour les paramètres
with st.sidebar:
    st.header("Configuration")
    
    algo_choice = st.selectbox(
        "Choisissez un algorithme",
        options=[
            ("First-Fit", "first-fit", first_fit),
            ("Best-Fit", "best-fit", best_fit),
            ("Min-Min", "min-min", min_min),
            ("Max-Min", "max-min", max_min),
            ("Genetic Algorithm (GA)", "genetic algorithm", genetic_algorithm),
        ],
        format_func=lambda x: x[0]
    )
    algo_display_name, algo_name, algo_function = algo_choice

    st.markdown("---")
    st.subheader("Données d'entrée")
    
    col1, col2 = st.columns(2)
    with col1:
        nb_services = st.number_input("Nombre de services", min_value=1, max_value=1000, value=100, step=10)
    with col2:
        nb_vms = st.number_input("Nombre de VMs", min_value=1, max_value=50, value=10, step=1)
    
    seed = st.number_input("Seed (pour reproductibilité)", value=123, step=1)
    
    st.markdown("---")
    run_button = st.button("🚀 Lancer l'algorithme", type="primary", use_container_width=True)

# Contenu principal
if run_button:
    with st.spinner(f"Exécution de {algo_display_name} en cours..."):
        start_time = time.time()
        
        # Génération des données
        services, vms_template = generate_random_data(nb_services, nb_vms, seed)
        
        # Copie propre des VMs
        vms = [VM(vm.id, vm.cpu_capacity, vm.ram_capacity) for vm in vms_template]
        
        # Exécution de l'algorithme
        if algo_name == "genetic algorithm":
            assignment, vms_result = algo_function(services, vms_template)
        else:
            assignment = algo_function(services.copy(), vms)
            vms_result = vms
        
        elapsed = time.time() - start_time
        
        # Calcul des métriques
        metrics = compute_metrics(vms_result, services)

    # === Affichage des résultats ===
    st.success(f"✅ {algo_display_name} terminé en {elapsed:.4f} secondes !")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Makespan", f"{metrics['makespan']:.2f}s")
    with col2:
        st.metric("Services placés", f"{metrics['assigned']}", f"/ {metrics['assigned'] + metrics['rejected']}")
    with col3:
        st.metric("Utilisation CPU", f"{metrics['cpu_util_%']:.1f}%")
    with col4:
        st.metric("Utilisation RAM", f"{metrics['ram_util_%']:.1f}%")

    st.markdown(f"### Répartition des services par VM ({algo_display_name})")

    # Tableau détaillé par VM
    vm_data = []
    for vm in sorted(vms_result, key=lambda x: x.id):
        service_ids = [s.id for s in vm.services]
        vm_data.append({
            "VM ID": vm.id,
            "Nb Services": len(service_ids),
            "Services": ", ".join(map(str, sorted(service_ids))) if service_ids else "-",
            "Makespan VM": round(vm.completion_time, 2),
            "CPU utilisé": f"{(vm.cpu_used()/vm.cpu_capacity):.3f}",
            "RAM utilisé": f"{(vm.ram_used()/vm.ram_capacity):.3f}",
        })
    
    df_vms = pd.DataFrame(vm_data)
    st.dataframe(df_vms, use_container_width=True, hide_index=True)

    # === Graphiques ===
    st.markdown("### Visualisations")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Makespan par VM")
        fig, ax = plt.subplots(figsize=(10, 5))
        vm_ids = [vm.id for vm in sorted(vms_result, key=lambda x: x.id)]
        makespans = [vm.completion_time for vm in sorted(vms_result, key=lambda x: x.id)]
        bars = ax.bar(vm_ids, makespans, color=sns.color_palette("viridis", len(vm_ids)))
        ax.set_xlabel("VM ID")
        ax.set_ylabel("Makespan (s)")
        ax.set_title("Temps de complétion par VM")
        ax.axhline(y=metrics['makespan'], color='r', linestyle='--', label=f'Makespan global = {metrics["makespan"]:.2f}')
        ax.legend()
        st.pyplot(fig)
        plt.close()

    with col2:
        st.subheader("Charge par VM")
        load_data = [
            {"VM": vm.id, "Ressource": "CPU", "Utilisation (%)": (vm.cpu_used() / vm.cpu_capacity) * 100}
            for vm in vms_result
        ] + [
            {"VM": vm.id, "Ressource": "RAM", "Utilisation (%)": (vm.ram_used() / vm.ram_capacity) * 100}
            for vm in vms_result
        ]
        df_load = pd.DataFrame(load_data)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=df_load, x="VM", y="Utilisation (%)", hue="Ressource", ax=ax, palette="Set2")
        ax.set_title("Utilisation CPU & RAM par VM")
        ax.legend(title="Ressource")
        st.pyplot(fig)
        plt.close()

    # === Résumé texte (comme print_results original) ===
    with st.expander("Affichage console-style (comme avant)"):
        st.code(f"""
==========================================================================
                        {algo_display_name.upper()}
==========================================================================
Temps d'exécution     : {elapsed:.4f}s
Makespan              : {metrics['makespan']:.2f}
Services placés       : {metrics['assigned']}/{metrics['assigned'] + metrics['rejected']}
Utilisation           : CPU {metrics['cpu_util_%']:.1f}% | RAM {metrics['ram_util_%']:.1f}%

Répartition par VM :
""")
        for vm in sorted(vms_result, key=lambda x: x.id):
            ids = [s.id for s in vm.services]
            st.code(f"  VM{vm.id:2d} : {len(ids)} services → [{', '.join(map(str, sorted(ids)))}]  (makespan={vm.completion_time:.1f})")

else:
    st.info("👈 Configurez les paramètres à gauche et cliquez sur **Lancer l'algorithme** pour commencer.")
    st.markdown("""
    ### Algorithmes disponibles :
    - **First-Fit** : Place le service dans la première VM qui a assez de ressources
    - **Best-Fit** : Place dans la VM avec le moins d'espace restant (meilleur ajustement)
    - **Min-Min** : Ordonnancement heuristique rapide
    - **Max-Min** : Variante favorisant les grandes tâches d'abord
    - **Genetic Algorithm** : Métaheuristique évolutionnaire (plus lent mais souvent meilleur)
    """)
