import time
import argparse
from utils.helpers import load_data, generate_random_data, compute_metrics, print_results
from algorithms.first_fit import first_fit
from algorithms.best_fit import best_fit
from algorithms.min_min import min_min
from algorithms.max_min import max_min
from algorithms.genetic import genetic_algorithm
from models.entities import VM

ALGOS = {
    "first-fit": first_fit,
    "best-fit": best_fit,
    "min-min": min_min,
    "max-min": max_min,
    "ga": genetic_algorithm
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloud Assignment Project")
    parser.add_argument("--algos", nargs="+", default=["first-fit", "best-fit", "min-min", "ga"],
                        choices=ALGOS.keys(), help="Algorithmes à exécuter")
    parser.add_argument("--data", choices=["random", "file"], default="random")
    parser.add_argument("--services", type=int, default=25)
    parser.add_argument("--vms", type=int, default=5)
    parser.add_argument("--seed", type=int, default=123)
    args = parser.parse_args()

    # Chargement des données
    if args.data == "file":
        services, vms_template = load_data()
    else:
        services, vms_template = generate_random_data(args.services, args.vms, args.seed)

        print(f"Jeu de donnees : {len(services)} services -> {len(vms_template)} VMs")
        print()  # ligne vide
    # Dans main.py → remplace la boucle for algo_name in args.algos par :

    for algo_name in args.algos:
      vms = [VM(vm.id, vm.cpu_capacity, vm.ram_capacity) for vm in vms_template]

      start = time.time()
      if algo_name == "ga":
            assignment, vms = genetic_algorithm(services, vms_template)  # ← on récupère les vraies VMs remplies
      else:
            assignment = ALGOS[algo_name](services, vms)
      elapsed = time.time() - start

      metrics = compute_metrics(vms, services)
      print_results(algo_name, assignment, vms, metrics, elapsed)
