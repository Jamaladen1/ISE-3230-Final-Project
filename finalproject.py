import gurobipy as gp
from gurobipy import GRB

# Movie data
movies = {
    1: {'name': 'Amazing Spiderman', 'length': 136, 'genre': 'Action', 'cost': 6.29, 'rating': 6.9},
    2: {'name': 'Night of the Museum', 'length': 108, 'genre': 'Adventure', 'cost': 3.99, 'rating': 6.4},
    3: {'name': 'Cheaper by the Dozen', 'length': 98,  'genre': 'Comedy',    'cost': 3.00, 'rating': 5.9},
    4: {'name': 'Hidden Figures',      'length': 127, 'genre': 'Drama',      'cost': 4.99, 'rating': 7.8}
}

# Person preferences
person_preferences = {
    1: {'length': (90, 130),  'cost': (0, 7),  'rating': (6, 10), 'genres': ['Action', 'Comedy']},
    2: {'length': (100, 160), 'cost': (0, 12), 'rating': (7, 10), 'genres': ['Drama', 'Thriller', 'Romance']},
    3: {'length': (80, 110),  'cost': (0, 10), 'rating': (5, 8),  'genres': ['Horror', 'Sci-Fi']},
    4: {'length': (95, 150),  'cost': (0, 8),  'rating': (6, 9),  'genres': ['Comedy', 'Animation', 'Adventure']},
    5: {'length': (70, 120),  'cost': (0, 5),  'rating': (4, 7),  'genres': ['Action', 'Documentary']}
}


# MODEL

m = gp.Model("movie_selection")
m.Params.LogToConsole = 1

# Decision variables
x = m.addVars(4, vtype=GRB.BINARY, name="x")

# Precompute satisfaction indicators
Lp_indicators, Gp_indicators, Cp_indicators, Rp_indicators = {}, {}, {}, {}

for p in range(1, 6):
    Lp_indicators[p] = []
    Gp_indicators[p] = []
    Cp_indicators[p] = []
    Rp_indicators[p] = []

    prefs = person_preferences[p]

    for i in range(4):
        movie = movies[i + 1]

        # Length
        Lp_indicators[p].append(int(prefs['length'][0] <= movie['length'] <= prefs['length'][1]))

        # Genre
        Gp_indicators[p].append(int(movie['genre'] in prefs['genres']))

        # Cost
        Cp_indicators[p].append(int(prefs['cost'][0] <= movie['cost'] <= prefs['cost'][1]))

        # Rating
        Rp_indicators[p].append(int(prefs['rating'][0] <= movie['rating'] <= prefs['rating'][1]))


# Hp CALCULATIONS

H = {}

for p in range(1, 6):
    Lp = gp.quicksum(x[i] * Lp_indicators[p][i] for i in range(4))
    Gp = gp.quicksum(x[i] * Gp_indicators[p][i] for i in range(4))
    Cp = gp.quicksum(x[i] * Cp_indicators[p][i] for i in range(4))
    Rp = gp.quicksum(x[i] * Rp_indicators[p][i] for i in range(4))

    H[p] = (Lp + Gp + Cp + Rp) / 4

# OBJECTIVE

m.setObjective(gp.quicksum(H[p] for p in range(1, 6)), GRB.MAXIMIZE)


# CONSTRAINTS

# Select exactly one movie
m.addConstr(x.sum('*') == 1, "select_one")

# Each person must satisfy at least 2 out of 4 preferences (Hp ≥ 0.5)
for p in range(1, 6):
    m.addConstr(H[p] >= 0.5, name=f"pref_{p}")


# SOLVE

m.optimize()


# RESULTS

print("\nObjective value =", m.ObjVal)

print("\nMovie selection:")
for i in range(4):
    if x[i].X > 0.5:
        print(f"Selected movie {i+1}: {movies[i+1]['name']}")

print("\nPreference satisfaction:")
for p in range(1, 6):
    print(f"Person {p}: Hp = {H[p].getValue():.4f}")
