# ☁️ Optimisation de l'affectation des ressources dans le Cloud

## 📋 Description du Projet

Ce projet est une **application web interactive** (Streamlit) qui implémente et teste **5 algorithmes d'ordonnancement** pour résoudre le problème classique du **Cloud Resource Allocation**. L'objectif est d'affecter efficacement une liste de services (tâches informatiques) à des machines virtuelles (VMs) en minimisant le temps total d'exécution (**makespan**) et en optimisant l'utilisation des ressources (CPU et RAM).

### 🎯 Problème résolu
**Service-to-VM Scheduling Problem** : Comment distribuer intelligemment des services demandant diverses ressources (CPU, RAM) et des temps d'exécution à des VMs de capacités limitées ?

---

## 🚀 Installation et Exécution

### Prérequis
- **Python 3.8+** installé
- **Accès à internet** (pour télécharger les dépendances)

### Étapes d'installation (Windows PowerShell)

```powershell
# 1. Naviguer vers le dossier du projet
cd "c:\Users\xps\OneDrive\Bureau\projet_RO\Projet-RO"

# 2. Installer les dépendances
pip install streamlit deap pandas matplotlib seaborn

# 3. Lancer l'application
streamlit run app.py
```

L'application **s'ouvrira automatiquement** dans votre navigateur à `http://localhost:8501`

---

## 📁 Structure du Projet

```
Projet-RO/
├── app.py                          # Application Streamlit (interface web)
├── README.md                        # Documentation
├── 
├── algorithms/                      # Implémentations des algorithmes
│   ├── first_fit.py                 # Heuristique 1 : First-Fit
│   ├── best_fit.py                  # Heuristique 2 : Best-Fit
│   ├── min_min.py                   # Heuristique 3 : Min-Min
│   ├── max_min.py                   # Heuristique 4 : Max-Min
│   └── genetic.py                   # Métaheuristique : Algorithme Génétique
│
├── models/
│   └── entities.py                  # Classes Service et VM
│
├── utils/
│   └── helpers.py                   # Fonctions utilitaires (chargement, calcul métriques)
│
└── data/                            # Fichiers JSON pour données d'entrée
    ├── services.json                # Liste des services (25 services pré-définis)
    └── vms.json                     # Liste des VMs (5 VMs pré-définis)
```

---

## 📊 Description détaillée des 5 Algorithmes

### 1️⃣ **First-Fit** (Heuristique simple)
- **Principe** : Parcourt les services un par un. Assigne chaque service à la **première VM** qui a assez de ressources libres.
- **Complexité** : O(n × m) — **très rapide**
- **✅ Avantages** : Très simple, exécution quasi-instantanée
- **❌ Inconvénients** : Très sensible à l'ordre des services, fragmentation importante des ressources

### 2️⃣ **Best-Fit** (Heuristique améliorée)
- **Principe** : Pour chaque service, choisit la VM où il restera **le moins de ressources libres** après placement (meilleure compaction).
- **Complexité** : O(n × m)
- **✅ Avantages** : Meilleure utilisation des ressources que First-Fit
- **❌ Inconvénients** : Peut créer des "trous" trop petits pour les services suivants

### 3️⃣ **Min-Min** (Heuristique équilibrée)
- **Principe** :
  1. Parmi les services non affectés, cherche celui avec le **temps d'exécution minimum**
  2. L'assigne à la VM qui minimise son makespan (temps de fin)
  3. Répète jusqu'à ce que tous les services soient affectés
- **✅ Avantages** : Bon makespan global, équilibre des charges
- **❌ Inconvénients** : Les gros services se retrouvent à la fin

### 4️⃣ **Max-Min** (Heuristique équitable)
- **Principe** : Identique à Min-Min, mais on place en priorité les services ayant le **temps d'exécution maximum**.
- **✅ Avantages** : Meilleur équilibre, pas de report des grosses tâches
- **❌ Inconvénients** : Léger compromis sur le makespan

### 5️⃣ **Algorithme Génétique (GA)** ⭐ Métaheuristique
- **Représentation** : Chaque solution = liste où `solution[i] = ID de la VM` affectée au service i
- **Opérateurs génétiques** :
  - **Sélection** : Tournoi (3 individus)
  - **Croisement** : Deux points
  - **Mutation** : Réaffectation aléatoire (20% de probabilité par gène)
- **Paramètres** :
  - Population : 100 individus (ajustable)
  - Générations : 200 (ajustable)
  - Probabilité croisement : 0.7
  - Probabilité mutation : 0.3
- **3 modes d'optimisation** :
  - `makespan` : Minimise le temps total
  - `vms` : Minimise le nombre de VMs utilisées
  - `hybrid` : Compromis (70% temps + 30% VMs utilisées)
- **✅ Avantages** : Trouve des solutions bien meilleures que les heuristiques
- **❌ Inconvénients** : Plus lent (quelques secondes)

---

## 🎮 Guide d'utilisation de l'application

### Interface

**Barre latérale gauche (Sidebar)** :
1. Choisir un algorithme dans le dropdown
2. Configurer le nombre de services et VMs
3. Définir un seed pour la reproductibilité
4. **Si Algorithme Génétique** : ajuster les paramètres (population, générations, objectif)

**Boutons** :
- 🚀 **Lancer l'algorithme** : Exécute l'algorithme sélectionné
- 🔄 **Comparer tous les algos** : Lance les 5 algorithmes et compare les résultats

### Résultats affichés

Après exécution :
- **Cartes de métriques** : Makespan, services assignés/rejetés, utilisation CPU/RAM
- **Tableau détaillé** : Répartition par VM (services affectés, ressources utilisées)
- **Graphiques** : Visualisation de l'utilisation des ressources et distribution des services
- **Console-style** : Affichage détaillé des résultats

---

## 📈 Métriques d'évaluation

| Métrique | Description | Unité |
|----------|-----------|-------|
| **Makespan** | Temps d'exécution total = charge maximale sur une VM | secondes |
| **Services assignés** | Nombre de services placés avec succès | nombre |
| **Services rejetés** | Services non affectés faute de ressources | nombre |
| **Utilisation CPU** | Pourcentage moyen de CPU utilisé | % |
| **Utilisation RAM** | Pourcentage moyen de RAM utilisé | % |
| **Temps d'exécution algo** | Performance de l'algorithme lui-même | secondes |

---

## 💾 Format des données d'entrée

### `data/vms.json` - Machines Virtuelles
```json
[
  {"id": 0, "cpu_capacity": 20, "ram_capacity": 64},
  {"id": 1, "cpu_capacity": 16, "ram_capacity": 32}
]
```
- `cpu_capacity` : CPU disponible (unités)
- `ram_capacity` : RAM disponible (GB)

### `data/services.json` - Services/Tâches
```json
[
  {"id": 0, "cpu": 3.2, "ram": 8.0, "exec_time": 18.5},
  {"id": 1, "cpu": 1.8, "ram": 4.0, "exec_time": 12.3}
]
```
- `cpu` : CPU demandé
- `ram` : RAM demandée
- `exec_time` : Temps d'exécution

---

## 🔧 Fonctionnalités principales

✅ **Génération aléatoire** : Créez de nouveaux jeux de données avec différents seeds  
✅ **Comparaison multi-algorithmes** : Testez les 5 approches sur le même dataset  
✅ **Interface interactive** : Ajustez les paramètres en temps réel  
✅ **Visualisations graphiques** : Histogrammes et courbes de performance  
✅ **Reproductibilité** : Les seeds assurent des résultats constants  

---

## 💡 Exemple de flux d'utilisation

1. **Lancer Streamlit** → Interface se charge
2. **Choisir un algorithme** (ex: First-Fit)
3. **Définir nb_services=25, nb_vms=5, seed=123**
4. **Cliquer "🚀 Lancer"**
5. **Observer les résultats** : makespan, métriques, graphiques
6. **Tester les autres algos** avec les mêmes paramètres
7. **Comparer** avec le bouton 🔄 pour voir quel algo est le meilleur

---

## 📚 Dépendances Python

```
streamlit       → Interface web interactive
deap            → Framework pour algorithmes génétiques
pandas          → Manipulation de données
matplotlib      → Graphiques
seaborn         → Styles de graphiques
```

---

## 🎓 Concepts clés

| Terme | Signification |
|-------|--------------|
| **Makespan** | Temps total = max(temps de chaque VM) |
| **Allocation** | Affectation d'un service à une VM |
| **Fitness** | Qualité d'une solution (ici = makespan) |
| **Heuristique** | Algorithme rapide mais non-optimal |
| **Métaheuristique** | Technique pour améliorer les heuristiques |

---

## ✨ Notes importantes

- **Exécution séquentielle** : Les services d'une VM s'exécutent l'un après l'autre
- **VMs homogènes** : Même puissance de calcul pour tous
- **Pas de migration** : Un service, une fois affecté, reste sur sa VM
- **Réinitialisation** : Les VMs sont réinitialisées entre chaque exécution d'algorithme

---

Vous pouvez maintenant **lancer l'application et explorer les différents algorithmes** ! 🚀
