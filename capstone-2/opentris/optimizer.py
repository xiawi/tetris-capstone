# Implement GA here, but future research can use whatever optimization algorithm they want.

import random
import copy
from gamemanager import GameManager
from concurrent.futures import ThreadPoolExecutor

WEIGHT_VECTOR_SIZE = 9 # focusing on 9 numerical features, therefore 9 weights in the vector
POPULATION_SIZE = 6
MUTATION_RATE = 0.1
MAX_ITER = 10000
MIN_AVERAGE_DIFFERENCE = 0.01

class GAOptimizer:
  def __init__(self) -> None:
    self.population = self.initializePopulation()
    self.fitnesses = self.calculateFitnesses(self.population)
    self.runGA()
    pass
  
  def initializePopulation(self):
    population = []
    for i in range(POPULATION_SIZE):
      individual = [] # individual represented as weight vectors
      for j in range(WEIGHT_VECTOR_SIZE):
        individual.append(random.uniform(-1,1))
      population.append(individual)
    return population

  def calculateFitnesses(self, population):
    fitness = [0] * POPULATION_SIZE
    individual_wins = [[0 for _ in range(POPULATION_SIZE)] for _ in range(POPULATION_SIZE)]
    individual_attacks = [[0 for _ in range(POPULATION_SIZE)] for _ in range(POPULATION_SIZE)]

    # Function to simulate a single match
    def simulate_match(i, j):
      print(".", end="", flush=True)  # Print a dot for each game
      game_manager = GameManager(False, population[i], population[j])
      results = game_manager.run()  # results = (winner, attack1, attack2)
      print("!", end="", flush=True)
      return i, j, results[0], results[1], results[2]

    # Create tasks for matches
    matches = [(i, j) for i in range(POPULATION_SIZE - 1) for j in range(i + 1, POPULATION_SIZE)]

    # Run matches in parallel using ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
      results = list(executor.map(lambda match: simulate_match(*match), matches))

    # Process match results
    for i, j, winner, attack_by_i, attack_by_j in results:
      if winner == 0:
        individual_wins[i][j] = 1
      else:
        individual_wins[j][i] = 1
      individual_attacks[i][j] = attack_by_i
      individual_attacks[j][i] = attack_by_j

    # Calculate fitness
    for i in range(POPULATION_SIZE):
      total_wins = sum(individual_wins[i])
      total_attack_efficiency = sum(individual_attacks[i])
      winrate = total_wins / (POPULATION_SIZE - 1)  # Matches played
      average_efficiency = total_attack_efficiency / (POPULATION_SIZE - 1)
      fitness[i] = winrate + 5 * average_efficiency

    print("\nfitness calculated")  # Move to a new line after all games are printed
    return fitness

  def selectParents(self, population, fitnesses):
    parent_pair = []
    cumulative_fitness = [0] * POPULATION_SIZE
    cumulative_fitness[0] = fitnesses[0]
    for i in range(1, POPULATION_SIZE):
      cumulative_fitness[i] = cumulative_fitness[i - 1] + fitnesses[i]
  
    for i in range(2):
      rand = random.uniform(0, cumulative_fitness[-1])
      for j in range(len(cumulative_fitness)):
          if rand <= cumulative_fitness[j]:
            parent_pair.append(population[j])
            break
    return parent_pair
  
  def crossover(self, parents):
    child1 = copy.deepcopy(parents[0])
    child2 = copy.deepcopy(parents[1])

    for i in range(WEIGHT_VECTOR_SIZE):
      rand = random.random()
      if rand > 0.5:
        temp = child1[i]
        child1[i] = child2[i]
        child2[i] = temp

    return [child1, child2]
  
  def mutate(self, individual):
    for i in range(len(individual)):
      rand = random.random()
      if rand < MUTATION_RATE:
        individual[i] += random.uniform(-0.1, 0.1)
        if individual[i] > 1:
          individual[i] = 1
        elif individual[i] < -1:
          individual[i] = -1
    return individual
  
  def findAverageDifferences(self, population):
    average_differences = []
    for i in range(POPULATION_SIZE - 1):
      differences = []
      for j in range(i, POPULATION_SIZE):
        for k in range(WEIGHT_VECTOR_SIZE):
          differences.append(abs(population[i][k] - population[j][k]))
      average_differences.append(sum(differences)/len(differences))
    
    return sum(average_differences)/len(average_differences)

  def runGA(self):
    curr_iter = 0
    
    while (curr_iter < MAX_ITER and self.findAverageDifferences(self.population) > MIN_AVERAGE_DIFFERENCE):
      curr_iter += 1
      new_generation = []
      for i in range(int(POPULATION_SIZE/2)):
        parents = self.selectParents(self.population, self.fitnesses)
        offspring = self.crossover(parents)
        new_generation.extend(offspring)
      mutated = [self.mutate(offspring) for offspring in new_generation]
      self.population = mutated
      self.fitnesses = self.calculateFitnesses(self.population)
      max_fitness = max(self.fitnesses)
      print(self.population[self.fitnesses.index(max_fitness)], max_fitness)
   
    if curr_iter >= MAX_ITER:
      print("max iterations reached")
    else:
      print("convergence occured")
  
if __name__ == "__main__":
  ga = GAOptimizer()