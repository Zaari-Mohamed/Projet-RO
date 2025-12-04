# algorithms/genetic.py
import random
from typing import List, Dict
from deap import base, creator, tools
from models.entities import Service, VM

# Création des classes DEAP (une seule fois)
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

def genetic_algorithm(services: List[Service], vms_template: List[VM],
                      pop_size=100, generations=200, cxpb=0.7, mutpb=0.3) -> Dict[int, int]:
    n_services = len(services)
    n_vms = len(vms_template)

    # Outils DEAP
    toolbox = base.Toolbox()
    toolbox.register("vm_id", random.randint, 0, n_vms - 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.vm_id, n_services)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def evaluate(individual):
        # Création de VMs temporaires pour évaluer cette solution
        temp_vms = [VM(vm.id, vm.cpu_capacity, vm.ram_capacity) for vm in vms_template]
        for svc_idx, vm_idx in enumerate(individual):
            svc = services[svc_idx]
            if not temp_vms[vm_idx].can_host(svc):
                return (10**9,)  # pénalité énorme si invalide
            temp_vms[vm_idx].assign(svc)
        makespan = max(vm.completion_time for vm in temp_vms)
        return (makespan,)

    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=n_vms-1, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Évolution
    pop = toolbox.population(n=pop_size)
    for gen in range(generations):
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < cxpb:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < mutpb:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Évaluation des nouveaux individus
        invalid = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid)
        for ind, fit in zip(invalid, fitnesses):
            ind.fitness.values = fit

        pop[:] = offspring

    # Meilleur individu
    best = tools.selBest(pop, 1)[0]

    # ON RECONSTRUIT LES VRAIES VMs AVEC LA MEILLEURE SOLUTION
    final_vms = [VM(vm.id, vm.cpu_capacity, vm.ram_capacity) for vm in vms_template]
    assignment = {}
    for svc_idx, vm_idx in enumerate(best):
        svc = services[svc_idx]
        if final_vms[vm_idx].can_host(svc):  # can_host
            final_vms[vm_idx].assign(svc)
            assignment[svc.id] = final_vms[vm_idx].id

    # ON RETOURNE L'ASSIGNATION + ON REMPLACE LES VMS DANS main.py
    # → mais comme on ne peut pas modifier vms depuis ici, on retourne aussi les VMs remplis
    return assignment, final_vms