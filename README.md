# Projet-RO
Optimisation de l’affectation des ressources dans le Cloud Computing

# explication des algos : 
### 1. First-Fit  
- **Principe** : Parcourt les services dans l'ordre donné. Pour chaque service, l'assigne à la **première VM** qui a assez de ressources libres.
- **Complexité** : O(n × m) — très rapide
- **Avantages** : Extrêmement simple et rapide
- **Inconvénients** : Très sensible à l'ordre des services → fragmentation importante

### 2. Best-Fit  
- **Principe** : Pour chaque service, choisit la VM qui aura **le moins de ressources libres restantes** après placement (minimise le "gaspillage").
- **Complexité** : O(n × m)
- **Avantages** : Meilleure compaction que First-Fit dans la plupart des cas
- **Inconvénients** : Peut créer des "trous" trop petits pour les gros services futurs

### 3. Min-Min  
- **Principe** :  
  1. Pour chaque service non placé, calcule le temps de fin minimum possible sur toutes les VMs disponibles  
  2. Place en priorité le service ayant le **temps minimum global**  
- **Avantages** : Très bon makespan, favorise les petites tâches rapides
- **Inconvénients** : Peut laisser les grosses tâches pour la fin → déséquilibre

### 4. Max-Min  
- **Principe** : Identique à Min-Min, mais on place en priorité le service ayant le **temps maximum** (version "fair")
- **Avantages** : Évite de reporter les grosses tâches à la fin → meilleur équilibre
- **Inconvénients** : Légèrement moins bon makespan que Min-Min dans certains cas

### 5. Algorithme Génétique (GA) — Métaheuristique  
- **Représentation** : Un individu = liste d'entiers où `individu[i] = ID de la VM` affectée au service i
- **Fitness** : Makespan (max charge d'une VM). Pénalité forte si un placement est impossible
- **Opérateurs** :
  - Sélection par tournoi
  - Croisement en deux points
  - Mutation uniforme (réaffectation aléatoire d'une tâche)
- **Paramètres par défaut** : pop=100, gén=200, cx=0.7, mut=0.3
- **Avantages** : Capable de trouver de meilleures solutions que les heuristiques, surtout sur instances difficiles
- **Inconvénients** : Plus lent (quelques secondes)

## Métriques d'évaluation
| Métrique                  | Description |
|--------------------------|-----------|
| Makespan                 | Temps total = charge maximale d'une VM |
| Services assignés / rejetés | Nombre de tâches placées |
| Utilisation moyenne CPU/RAM | % de ressources utilisées |
| Temps d'exécution de l'algo | Performance algorithmique |
