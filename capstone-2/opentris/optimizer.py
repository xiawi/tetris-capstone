# Implement GA here, but future research can use whatever optimization algorithm they want.

import random
import copy
from gamemanager import GameManager
from concurrent.futures import ThreadPoolExecutor

WEIGHT_VECTOR_SIZE = 10 # focusing on 10 numerical features, therefore 10 weights in the vector
POPULATION_SIZE = 6
MUTATION_RATE = 0.1
MAX_ITER = 10000
MIN_AVERAGE_DIFFERENCE = 0.01

class GAOptimizer:
  def __init__(self) -> None:
    self.population_log_file = open("./logs/08_12_06_2_indivs_population_log.txt", "w", buffering=1)
    self.best_individual_log_file = open("./logs/08_12_06_2_indivs_best_individual_log.txt", "w", buffering=1)
  
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
    # individual_wins = [[0 for _ in range(POPULATION_SIZE)] for _ in range(POPULATION_SIZE)]
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
      # if winner == 0:
      #   individual_wins[i][j] = 1
      # else:
      #   individual_wins[j][i] = 1
      individual_attacks[i][j] = attack_by_i
      individual_attacks[j][i] = attack_by_j

    # Calculate fitness
    for i in range(POPULATION_SIZE):
      # total_wins = sum(individual_wins[i])
      total_attack_efficiency = sum(individual_attacks[i])
      # winrate = total_wins / (POPULATION_SIZE - 1)  # Matches played
      average_efficiency = total_attack_efficiency / (POPULATION_SIZE - 1)
      fitness[i] = average_efficiency

    print("\nfitness calculated") 
    return fitness

  # def selectParents(self, population, fitnesses):
  #   parent_pair = []
  #   cumulative_fitness = [0] * POPULATION_SIZE
  #   cumulative_fitness[0] = fitnesses[0]
  #   for i in range(1, POPULATION_SIZE):
  #     cumulative_fitness[i] = cumulative_fitness[i - 1] + fitnesses[i]
  
  #   for i in range(2):
  #     rand = random.uniform(0, cumulative_fitness[-1])
  #     for j in range(len(cumulative_fitness)):
  #         if rand <= cumulative_fitness[j]:
  #           parent_pair.append(population[j])
  #           break
  #   return parent_pair
  
  def selectParents(self, population, fitnesses):
    # Pair fitnesses with their indices and sort by fitness
    fitness_with_indices = sorted((f, i) for i, f in enumerate(fitnesses))
    
    # Generate dense ranks for sorted fitnesses
    ranks = [0] * len(fitnesses)  # Initialize ranks
    current_rank = 1  # Start rank from 1
    for i in range(len(fitness_with_indices)):
      if i > 0 and fitness_with_indices[i][0] != fitness_with_indices[i - 1][0]:
        current_rank = i + 1  # Increment rank only if fitness differs
      ranks[fitness_with_indices[i][1]] = current_rank

    # Calculate selection probabilities using ranks
    total_rank_sum = sum(ranks)
    selection_probs = [rank / total_rank_sum for rank in ranks]

    # Use roulette-wheel selection based on ranks
    parent_pair = []
    for _ in range(2):  # Select two parents
      rand = random.uniform(0, 1)
      cumulative_prob = 0
      for i, prob in enumerate(selection_probs):
        cumulative_prob += prob
        if rand <= cumulative_prob:
          parent_pair.append(population[i])
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
  
  def logPopulation(self, population, fitnesses, iteration):
    self.population_log_file.write(f"Iteration {iteration}:\n")
    for ind, fit in zip(population, fitnesses):
        self.population_log_file.write(f"Individual: {ind}, Fitness: {fit}\n")
    self.population_log_file.write("\n")
    self.population_log_file.flush()  # Ensure immediate saving

  def logBestIndividual(self, best_individual, best_fitness, iteration):
    self.best_individual_log_file.write(f"Iteration {iteration}: Best Individual: {best_individual}, Fitness: {best_fitness}\n")
    self.best_individual_log_file.flush()  # Ensure immediate saving

  def runGA(self):
    self.population = self.initializePopulation()
    self.fitnesses = self.calculateFitnesses(self.population)
    curr_iter = 0
    
    while (curr_iter < MAX_ITER and self.findAverageDifferences(self.population) > MIN_AVERAGE_DIFFERENCE):
      curr_iter += 1

      max_fitness = max(self.fitnesses)
      best_individual = self.population[self.fitnesses.index(max_fitness)]

      self.logPopulation(self.population, self.fitnesses, curr_iter)
      self.logBestIndividual(best_individual, max_fitness, curr_iter)

      new_generation = []
      for i in range(int(POPULATION_SIZE/2)):
        parents = self.selectParents(self.population, self.fitnesses)
        offspring = self.crossover(parents)
        new_generation.extend(offspring)
      mutated = [self.mutate(offspring) for offspring in new_generation]
      self.population = mutated
      self.fitnesses = self.calculateFitnesses(self.population)
   
    if curr_iter >= MAX_ITER:
      print("max iterations reached")
    else:
      print("convergence occured")

    max_fitness = max(self.fitnesses)
    best_individual = self.population[self.fitnesses.index(max_fitness)]

    self.logPopulation(self.population, self.fitnesses, curr_iter)
    self.logBestIndividual(best_individual, max_fitness, curr_iter)
  
if __name__ == "__main__":
  ga = GAOptimizer()
  ga.runGA()