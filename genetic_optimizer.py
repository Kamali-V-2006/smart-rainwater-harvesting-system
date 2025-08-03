from deap import base, creator, tools, algorithms
import random

# Initial conditions
MAX_CAPACITY = 10000      # Max tank capacity in liters
initial_level = 6000      # Starting tank level (can also be from LSTM)
forecasted_rain = 3500    # 7-day forecasted inflow from LSTM or historical avg

# Fitness: Maximize usage without overflow
def fitness(individual):
    total_used = sum(individual)
    overflow = max(0, initial_level + forecasted_rain - total_used - MAX_CAPACITY)
    return total_used - overflow,  # Maximize this value

# DEAP setup
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr", lambda: random.randint(250, 500))  # Daily usage
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr, n=7)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", fitness)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutUniformInt, low=250, up=500, indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# Run the GA
pop = toolbox.population(n=20)
algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.2, ngen=40, verbose=False)

best = tools.selBest(pop, 1)[0]

# Show the result
print("✅ Optimized Daily Usage Schedule (liters):")
for i, day in enumerate(best, 1):
    print(f"Day {i}: {day} L")
print(f"Total Weekly Usage: {sum(best)} L")
