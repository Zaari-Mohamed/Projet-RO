import time
from utils.helpers import load_data, generate_random_data, compute_metrics, print_results
from algorithms.first_fit import first_fit
from algorithms.best_fit import best_fit
from algorithms.min_min import min_min
from algorithms.max_min import max_min
from algorithms.genetic import genetic_algorithm
from models.entities import VM

ALGOS = {
    "1": ("first-fit", first_fit),
    "2": ("best-fit", best_fit),
    "3": ("min-min", min_min),
    "4": ("max-min", max_min),
    "5": ("genetic algorithm", genetic_algorithm),
}

def user_menu():
    print("\n===== Cloud Assignment System =====\n")
    print("Choisissez un algorithme :")
    print("  1) First-Fit")
    print("  2) Best-Fit")
    print("  3) Min-Min")
    print("  4) Max-Min")
    print("  5) Genetic Algorithm (GA)")

    algo_choice = input("\nVotre choix (1-5) : ").strip()
    while algo_choice not in ALGOS:
        algo_choice = input("Choix invalide, réessayez (1-5) : ").strip()

    algo_name, algo_function = ALGOS[algo_choice]

    print("\n--- Paramètres des données ---")

    try:
        services = int(input("Nombre de services : "))
        vms = int(input("Nombre de machines (VMs) : "))
        seed = int(input("Seed (aléatoire) : "))
    except ValueError:
        print("Valeur invalide, utilisation des valeurs par défaut")
        services, vms, seed = 25, 7, 123

    return algo_name, algo_function, services, vms, seed


if __name__ == "__main__":

    # Menu interactif
    algo_name, algo_function, nb_services, nb_vms, seed = user_menu()

    # Génération des données
    services, vms_template = generate_random_data(nb_services, nb_vms, seed)

    print(f"\nJeu de données chargé : {len(services)} services -> {len(vms_template)} VMs\n")

    # Recréation des VMs vides pour chaque exécution
    vms = [VM(vm.id, vm.cpu_capacity, vm.ram_capacity) for vm in vms_template]

    # Exécution de l’algo
    print(f"⚙ Exécution de l'algorithme : {algo_name.upper()}\n")

    start = time.time()

    if algo_name == "genetic algorithm":
        assignment, vms = algo_function(services, vms_template)
    else:
        assignment = algo_function(services, vms)

    elapsed = time.time() - start

    # Calcul des métriques
    metrics = compute_metrics(vms, services)

    # Affichage
    print_results(algo_name, assignment, vms, metrics, elapsed)
