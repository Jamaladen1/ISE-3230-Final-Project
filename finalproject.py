import gurobi as gp
import numpy as np

# Movie data
# Movies: X1 = The Amazing Spiderman, X2 = Night at the Museum, 
#         X3 = Cheaper By the Dozen, X4 = Hidden Figures
movies = {
    1: {'name': 'Amazing Spiderman', 'length': 136, 'genre': 'Action', 'cost': 6.29, 'rating': 6.9},
    2: {'name': 'Night of the Museum', 'length': 108, 'genre': 'Adventure', 'cost': 3.99, 'rating': 6.4},
    3: {'name': 'Cheaper by the Dozen', 'length': 98, 'genre': 'Comedy', 'cost': 3.00, 'rating': 5.9},
    4: {'name': 'Hidden Figures', 'length': 127, 'genre': 'Drama', 'cost': 4.99, 'rating': 7.8}
}

# Person preferences (p = 1 to 5)
# Each person has preferred ranges for length, cost, rating, and preferred genres
# Format: {person: {'length': (min, max), 'cost': (min, max), 'rating': (min, max), 'genres': [list]}}
person_preferences = {
    1: {'length': (90, 130), 'cost': (0, 7), 'rating': (6, 10), 'genres': ['Action', 'Comedy']},
    2: {'length': (100, 160), 'cost': (0, 12), 'rating': (7, 10), 'genres': ['Drama', 'Thriller', 'Romance']},
    3: {'length': (80, 110), 'cost': (0, 10), 'rating': (5, 8), 'genres': ['Horror', 'Sci-Fi']},
    4: {'length': (95, 150), 'cost': (0, 8), 'rating': (6, 9), 'genres': ['Comedy', 'Animation', 'Adventure']},
    5: {'length': (70, 120), 'cost': (0, 5), 'rating': (4, 7), 'genres': ['Action', 'Documentary']}
}

# Decision variables: X[i] = 1 if movie i+1 is selected, 0 otherwise
x = gp.Variable(4, boolean=True)  # X1, X2, X3, X4

# Pre-compute preference indicators for each person and each movie
# Lp_i[p][i] = 1 if movie i's length satisfies person p's preference, 0 otherwise
# Similarly for Gp_i, Cp_i, Rp_i
Lp_indicators = {}
Gp_indicators = {}
Cp_indicators = {}
Rp_indicators = {}

for p in range(1, 6):  # p = 1 to 5
    Lp_indicators[p] = []
    Gp_indicators[p] = []
    Cp_indicators[p] = []
    Rp_indicators[p] = []
    
    prefs = person_preferences[p]
    
    for i in range(4):  # i = 0 to 3 (movies 1 to 4)
        movie = movies[i + 1]
        
        # Lp: check if length is in preferred range [Bp⁻, Bp⁺]
        length_min, length_max = prefs['length']
        if length_min <= movie['length'] <= length_max:
            Lp_indicators[p].append(1)
        else:
            Lp_indicators[p].append(0)
        
        # Gp: check if genre is in preferred genres
        if movie['genre'] in prefs['genres']:
            Gp_indicators[p].append(1)
        else:
            Gp_indicators[p].append(0)
        
        # Cp: check if cost is in preferred range [Bp⁻, Bp⁺]
        cost_min, cost_max = prefs['cost']
        if cost_min <= movie['cost'] <= cost_max:
            Cp_indicators[p].append(1)
        else:
            Cp_indicators[p].append(0)
        
        # Rp: check if rating is in preferred range [Bp⁻, Bp⁺]
        rating_min, rating_max = prefs['rating']
        if rating_min <= movie['rating'] <= rating_max:
            Rp_indicators[p].append(1)
        else:
            Rp_indicators[p].append(0)

# Calculate Hp for each person
# Hp = 1/4 * (Lp + Gp + Cp + Rp) where Lp, Gp, Cp, Rp are for the selected movie
H = []
for p in range(1, 6):  # p = 1 to 5
    # Lp = sum over movies of (x[i] * Lp_indicators[p][i])
    Lp = gp.sum([x[i] * Lp_indicators[p][i] for i in range(4)])
    Gp = gp.sum([x[i] * Gp_indicators[p][i] for i in range(4)])
    Cp = gp.sum([x[i] * Cp_indicators[p][i] for i in range(4)])
    Rp = gp.sum([x[i] * Rp_indicators[p][i] for i in range(4)])
    
    # Hp = 1/4 * (Lp + Gp + Cp + Rp)
    Hp = (Lp + Gp + Cp + Rp) / 4
    H.append(Hp)

# Objective: maximize sum of Hp for all people
obj_func = gp.sum(H)

# Constraints
constraints = []

# Constraint: Exactly one movie must be selected
constraints.append(gp.sum(x) == 1)

# Constraints: Each person must have at least 2 preferences met
# Note: Hp is between 0 and 1, so Hp >= 0.5 means at least 2 out of 4 preferences
# The image shows H₁ ≥ 2, but this likely means at least 2 preferences (Hp >= 0.5)
for p in range(5):  # p = 0 to 4 (representing persons 1 to 5)
    constraints.append(H[p] >= 0.5)  # At least 2 out of 4 preferences (0.5 = 2/4)

# Create and solve the problem
problem = gp.Problem(gp.Maximize(obj_func), constraints)

# Solve using GUROBI
problem.solve(solver=gp.GUROBI, verbose=True)

# Print results
print("obj_func =")
print(obj_func.value)
print("x =")
print(x.value)
print("\nSelected movie:")
for i in range(4):
    if x.value[i] > 0.5:
        print(f"Movie {i+1}: {movies[i+1]['name']}")
        print(f"  Length: {movies[i+1]['length']}, Genre: {movies[i+1]['genre']}, "
              f"Cost: {movies[i+1]['cost']}, Rating: {movies[i+1]['rating']}")

print("\nPreference satisfaction (Hp) for each person:")
for p in range(5):
    print(f"Person {p+1}: H{p+1} = {H[p].value:.4f}")
