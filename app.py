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
st.title("☁️ Optimisation de l'affectation des resources dans le Cloud ")

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
    
    # Afficher options GA uniquement si sélectionné
    if algo_name == "genetic algorithm":
        st.subheader("⚙️ Paramètres GA")
        ga_objective = st.selectbox(
            "Objectif de l'algorithme génétique",
            options=[
                ("Minimiser le Makespan (temps)", "makespan"),
                ("Minimiser les VMs utilisées", "vms"),
                ("Hybride (70% temps + 30% VMs)", "hybrid"),
            ],
            format_func=lambda x: x[0],
            help="Choisissez ce que vous voulez optimiser"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            ga_pop_size = st.slider("Taille population", min_value=20, max_value=200, value=100, step=10)
        with col2:
            ga_generations = st.slider("Générations", min_value=50, max_value=500, value=200, step=50)
    else:
        # Valeurs par défaut si pas GA
        ga_pop_size = 100
        ga_generations = 200
        ga_objective = ("Minimiser le Makespan (temps)", "makespan")
    
    st.markdown("---")
    run_button = st.button("🚀 Lancer l'algorithme", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 Comparaison")
    comparison_button = st.button("🔄 Comparer tous les algos", type="secondary", use_container_width=True)

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
            assignment, vms_result = algo_function(
                services, 
                vms_template,
                pop_size=ga_pop_size,
                generations=ga_generations,
                objective=ga_objective[1]  # Récupère le code (2ème élément du tuple)
            )
        else:
            assignment = algo_function(services.copy(), vms)
            vms_result = vms
        
        elapsed = time.time() - start_time
        
        # Calcul des métriques
        metrics = compute_metrics(vms_result, services)

    # === Affichage des résultats ===
    st.success(f"✅ {algo_display_name} terminé en {elapsed:.4f} secondes !")

    col1, col2, col3, col4 , col5 = st.columns(5)
    with col1:
        st.metric("Makespan", f"{metrics['makespan']:.2f}s")
    with col2:
        st.metric("Services placés", f"{metrics['assigned']}", f"/ {metrics['assigned'] + metrics['rejected']}")
    with col3:
        st.metric("Services rejetés", f"{metrics['rejected']}")
    with col4:
        st.metric("Utilisation CPU", f"{metrics['cpu_util_%']:.1f}%")
    with col5:
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
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap');

    .algo-card-premium {
        background: linear-gradient(145deg, #2d2d5a 0%, #1a1a3a 100%);
        padding: 30px;
        border-radius: 20px;
        color: #ffffff;
        margin-bottom: 25px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        border: 3px solid rgba(255, 255, 255, 0.15);
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        font-family: 'Poppins', sans-serif;
        position: relative;
        overflow: hidden;
    }

    .algo-card-premium::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: 0.5s;
    }

    .algo-card-premium:hover::before {
        left: 100%;
    }

    .algo-card-premium:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }

    .algo-title-premium {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 18px;
        letter-spacing: 0.5px;
        color: #ffffff;
    }

    .algo-desc-premium {
        font-size: 20px;
        opacity: 0.92;
        line-height: 1.6;
        font-weight: 600;
        color: #e6e6ff;
    }

    /* Couleurs spécifiques pour chaque carte */
    .ff-premium { background: linear-gradient(145deg, #2c3e50 0%, #34495e 100%) !important; }
    .bf-premium { background: linear-gradient(145deg, #8e44ad 0%, #9b59b6 100%) !important; }
    .mm-premium { background: linear-gradient(145deg, #2980b9 0%, #3498db 100%) !important; }
    .mxm-premium { background: linear-gradient(145deg, #d35400 0%, #e67e22 100%) !important; }
    .ga-premium { background: linear-gradient(145deg, #16a085 0%, #1abc9c 100%) !important; }
    .comp-premium { background: linear-gradient(145deg, #7f8c8d 0%, #95a5a6 100%) !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="algo-card-premium ff-premium">
            <div class="algo-title-premium">🔍 First-Fit</div>
            <div class="algo-desc-premium">Place le service dans la première VM disponible avec assez de ressources</div>
        </div>
        
        <div class="algo-card-premium bf-premium">
            <div class="algo-title-premium">🎯 Best-Fit</div>
            <div class="algo-desc-premium">Place dans la VM avec le moins d'espace restant (meilleur ajustement)</div>
        </div>
        
        <div class="algo-card-premium mm-premium">
            <div class="algo-title-premium">⚡ Min-Min</div>
            <div class="algo-desc-premium">Ordonnancement heuristique rapide - tâches courtes d'abord</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="algo-card-premium mxm-premium">
            <div class="algo-title-premium">📈 Max-Min</div>
            <div class="algo-desc-premium">Variante favorisant les grandes tâches d'abord</div>
        </div>
        
        <div class="algo-card-premium ga-premium">
            <div class="algo-title-premium">🧬 Genetic Algorithm</div>
            <div class="algo-desc-premium">Métaheuristique évolutionnaire - plus lent mais souvent meilleur</div>
        </div>
        
        <div class="algo-card-premium comp-premium">
            <div class="algo-title-premium">📊 Comparaison</div>
            <div class="algo-desc-premium">Testez et comparez les performances de chaque algorithme</div>
        </div>
        """, unsafe_allow_html=True)

# === SECTION COMPARAISON ===
if comparison_button:
    st.markdown("---")
    st.header("📊 Comparaison de tous les algorithmes")
    
    with st.spinner("Exécution de tous les algorithmes en cours..."):
        # Génération des données une seule fois
        services, vms_template = generate_random_data(nb_services, nb_vms, seed)
        
        # Résultats de tous les algos
        results = {}
        execution_times = {}
        
        algos_to_compare = [
            ("First-Fit", "first-fit", first_fit),
            ("Best-Fit", "best-fit", best_fit),
            ("Min-Min", "min-min", min_min),
            ("Max-Min", "max-min", max_min),
            ("Genetic Algorithm", "genetic algorithm", genetic_algorithm),
        ]
        
        for algo_display, algo_name, algo_func in algos_to_compare:
            start = time.time()
            
            # Copie propre des VMs
            vms = [VM(vm.id, vm.cpu_capacity, vm.ram_capacity) for vm in vms_template]
            
            # Exécution
            try:
                if algo_name == "genetic algorithm":
                    assignment, vms_result = algo_func(
                        services, 
                        vms_template,
                        pop_size=ga_pop_size,
                        generations=ga_generations,
                        objective=ga_objective[1]
                    )
                else:
                    assignment = algo_func(services.copy(), vms)
                    vms_result = vms
                
                elapsed = time.time() - start
                metrics = compute_metrics(vms_result, services)
                
                results[algo_display] = {
                    "metrics": metrics,
                    "vms": vms_result,
                    "assignment": assignment
                }
                execution_times[algo_display] = elapsed
            except Exception as e:
                st.warning(f"Erreur avec {algo_display}: {str(e)}")
        
        # === Affichage comparatif ===
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.subheader("⏱️ Temps d'exécution")
            fig, ax = plt.subplots(figsize=(8, 5))
            algos = list(execution_times.keys())
            times = list(execution_times.values())
            colors = sns.color_palette("husl", len(algos))
            ax.barh(algos, times, color=colors)
            ax.set_xlabel("Temps (secondes)")
            ax.set_title("Temps d'exécution")
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.subheader("⏱️ Makespan")
            fig, ax = plt.subplots(figsize=(8, 5))
            algos = list(results.keys())
            makespans = [results[a]["metrics"]["makespan"] for a in algos]
            colors = sns.color_palette("husl", len(algos))
            bars = ax.barh(algos, makespans, color=colors)
            ax.set_xlabel("Makespan (secondes)")
            ax.set_title("Temps total d'exécution")
            # Colorier le meilleur en vert
            best_idx = makespans.index(min(makespans))
            bars[best_idx].set_color('green')
            st.pyplot(fig)
            plt.close()
        
        with col3:
            st.subheader("🖥️ VMs utilisées")
            fig, ax = plt.subplots(figsize=(8, 5))
            algos = list(results.keys())
            vms_used = []
            for a in algos:
                num_vms = sum(1 for vm in results[a]["vms"] if vm.services)
                vms_used.append(num_vms)
            colors = sns.color_palette("husl", len(algos))
            bars = ax.barh(algos, vms_used, color=colors)
            ax.set_xlabel("Nombre de VMs utilisées")
            ax.set_title("Utilisation des VMs")
            # Colorier le meilleur (min) en vert
            best_idx = vms_used.index(min(vms_used))
            bars[best_idx].set_color('green')
            st.pyplot(fig)
            plt.close()
        
        with col4:
            st.subheader("📦 Services placés")
            fig, ax = plt.subplots(figsize=(8, 5))
            algos = list(results.keys())
            assigned = [results[a]["metrics"]["assigned"] for a in algos]
            colors = sns.color_palette("husl", len(algos))
            bars = ax.barh(algos, assigned, color=colors)
            ax.set_xlabel("Nombre de services")
            ax.set_title("Services placés / Total")
            # Colorier le meilleur (max) en vert
            best_idx = assigned.index(max(assigned))
            bars[best_idx].set_color('green')
            st.pyplot(fig)
            plt.close()
        
        # === Tableau récapitulatif ===
        st.markdown("---")
        st.subheader("📋 Tableau récapitulatif")
        
        comparison_data = []
        for algo_name in results.keys():
            m = results[algo_name]["metrics"]
            num_vms = sum(1 for vm in results[algo_name]["vms"] if vm.services)
            comparison_data.append({
                "Algorithme": algo_name,
                "Temps exécution (s)": f"{execution_times[algo_name]:.4f}",
                "Makespan (s)": m["makespan"],
                "Services placés": f"{m['assigned']}/{m['assigned'] + m['rejected']}",
                "VMs utilisées": num_vms,
                "CPU util. (%)": f"{m['cpu_util_%']:.1f}%",
                "RAM util. (%)": f"{m['ram_util_%']:.1f}%",
            })
        
        df_comparison = pd.DataFrame(comparison_data)
        st.dataframe(df_comparison, use_container_width=True, hide_index=True)
        
        st.success("✅ Comparaison complète !")

