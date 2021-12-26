from heapq import nlargest
import random
import sys
from time import time

from piece import QUEEN, ROOK, KNIGHT, BISHOP, PAWN
import evaluate_heuristic as eh

pieces_list = [ROOK, KNIGHT, BISHOP, PAWN]

def random_population(pop_size) -> 'List':
    '''
    Returns a list of dictionaries representing a population of pop_size heuristics

    pop_size --- Desired size of random population
    '''
    pop = []
    for i in range(pop_size):
        piece_values = []
        max_val = 0
        for piece in pieces_list:
            piece_values.append(random.random())
        max_val = max(piece_values)
        # We standard so that our max weight is 1
        if max_val != 0:
            for i in range(len(piece_values)):
                piece_values[i] /= max_val
        pop.append(piece_values)
    return pop
    
def select_most_fit(pop, fitness_dict, target_size, num_games, prob, depth) -> 'List':
    '''
    Given a population, it aims to return a subset of the poplation of size target_size
    that is the most fit
    Simplifies down to get K best problem with NlogK runtime

    pop --- Population, List
    fitness_dict --- Memo linking weight to its calculated fitness, dict
    target_size --- Desired size of population, int
    '''
    pop_size = len(pop)
    if target_size > pop_size:
        raise ValueError("select_most_fit --- can't return a subset that is greater in size")
    for weights in pop:
        # It's in our memo
        # if tuple(weights) in fitness_dict:
        #    continue

        def fxn(pos):
            return eh.value_based_heuristic(pos, weights)

        #vs_random = eh.compare_heuristic(fxn, eh.random_heuristic, num_games, prob, depth)
        vs_uniform = eh.compare_heuristic(fxn, eh.uniform_heuristic, num_games, prob, depth)
        # print(f"vs_random: {vs_random}, vs_uniform: {vs_uniform}, vs_simple: {vs_simple}")
        fitness_dict[tuple(weights)] = vs_uniform

    ret = nlargest(target_size, fitness_dict.keys(), key = fitness_dict.get)
    return list(map(lambda e: list(e), ret))

def cross_over(pop, offspring_size):
    '''
    Given a population, we want to conduct crossover and return offspring of size offspring_size
    We will implement uniform crossover

    pop --- Population that will serve as our parents, List
    offspring_size --- The number of offspring we want to generate from our parents
    '''
    offspring = []
    for i in range(offspring_size):
        offspring_weights = []
        parents = random.sample(pop, 2)
        for i in range(len(pieces_list)):
            # Conduct crossover

            # Uniform cut crossover
            # offspring_weights.append(parents[random.randint(0, 1)][i])

            # Blend crossover
            alpha = random.random()
            noise = random.uniform(-.05, .05)
            offspring_weights.append(alpha * parents[0][i] + (1 - alpha) * parents[1][i] + noise)

        max_val = max(offspring_weights)
        if max_val != 0:
            for i in range(len(offspring_weights)):
                offspring_weights[i] /= max_val
        offspring.append(offspring_weights)
    return offspring

def mutate(pop, mutation_rate) -> None:
    '''
    Given the population, it randomly mutates a few genes

    pop --- Population, List
    mutation_rate --- The chance that a mutation will occur for an attribute, float
    '''
    for i in range(len(pop)):
        for j in range(len(pop[0])):
            if random.random() < mutation_rate:
                pop[i][j] = random.random()

def round_list_values(lst, num_places):
    return list(map(lambda x: round(x, num_places), lst))

def breed(pop_size, num_generations, mutation_rate, num_games, prob, depth):
    '''
    Breeds a population of pop_size across num_generations generations
    At the end, return the best weights to give each piece and its corresponding fitness

    pop_size --- population size of each generation, int
    num_generations --- number of generation to run before done, int
    num_games --- the number of games each individual should play to determine 
        their fitness, int
    prob --- Probability that the agents will not play randomly, float
    depth --- Depth of minimax search, int
    '''
    start = time()
    fitness_dict = {}
    pop = random_population(pop_size)

    # While not done
    for i in range(num_generations):
        #print(f"Generation {i}:")
        #print("Evaluate each individual and select for crossover")
        parents = select_most_fit(pop, fitness_dict, pop_size // 4, num_games, prob, depth)
        # print("Parents:", parents)

        '''
        if i == 0: 
            best_weights = max(pop, key = lambda x: fitness_dict.get(tuple(x)))
            best_fitness = max([fitness_dict[tuple(w)] for w in pop])
            print(f"best_weights: {round_list_values(best_weights, 2)}")
            print(f"best_fitness: {best_fitness}")
            print(f"fitness: {sorted(round_list_values([fitness_dict[tuple(w)] for w in pop], 2))}")
        '''
        
        #print("Crossover")
        offspring = cross_over(parents, pop_size)
        # print("Offspring:", offspring)
        
        #print("Select for survival")
        # We include parents in the pool because we want to be at least as good as our last generation
        pop = select_most_fit(pop + offspring, fitness_dict, pop_size, num_games, prob, depth)
        
        '''
        print("-" * 50)
        best_weights = max(pop, key = lambda x: fitness_dict.get(tuple(x)))
        best_fitness = max([fitness_dict[tuple(w)] for w in pop])
        print(f"best_weights: {round_list_values(best_weights, 4)}")
        print(f"best_fitness: {best_fitness}")
        print(f"fitness: {sorted(round_list_values([fitness_dict[tuple(w)] for w in pop], 4))}")
        '''
        if i != num_generations - 1:
            mutate(pop, mutation_rate)

    best_weights = max(pop, key = lambda x: fitness_dict.get(tuple(x)))
    best_fitness = max([fitness_dict[tuple(w)] for w in pop])
    print(f"Breeding took {round(time() - start, 1)}s")
    return best_weights, best_fitness

def main():
    '''
    Handles command line input

    Users should run: ./MicroChessGeneticAlgorithm pop_size num_generations mutation_rate num_games prob depth
    '''
    argv = sys.argv

    pop_size = int(argv[1])
    num_generations = int(argv[2])
    mutation_rate = float(argv[3])
    num_games = int(argv[4])
    prob = float(argv[5])
    depth = int(argv[6])

    info = '''
I am currently running {0} generations of genetic algorithms for a population size
of {1} with a mutation rate of {2}. To determine fitness, I had
our genetically computed heuristics play against a uniform heuristic where each
game piece (rook, bishop, knight, pawn) are all worth the same in {3} games where
each agent employed a greedy strategy using their heuristic. In the comparison of 
the heuristics, we use our heuristic {4}% of the time and random play the rest of the time.
This operation may take ~15 minutes.
    '''.format(num_generations, pop_size, mutation_rate, num_games, prob * 100)
    print(info)

    best_weights, best_fitness = breed(pop_size, num_generations, mutation_rate, num_games, prob, depth)

    info = '''
I have finished running our evolutionary computation! I have determined the best weights
for the non-king pieces in microchess: {0} 
for rook, bishop, knight, and pawn respectively.

I will now investigate just how good our most fit heuristic is. Note that MicroChess frequently
leads to stalemates and draws which dilutes the win percentage of our most fit agent. I count
draws as half wins. 

Here is my most fit heuristic's win percentage against completely random play across 1000 games:
    '''.format(best_weights)
    print(info)

    def most_fit_fxn(pos):
        return eh.value_based_heuristic(pos, best_weights)
    
    print(eh.compare_heuristic(most_fit_fxn, eh.random_heuristic, 1000, prob, depth))

    info = '''
Here is my most fit heuristic's win percentage against a uniform heuristic where
each piece is valued equally across 1000 games:
    '''
    print(info)
    print(eh.compare_heuristic(most_fit_fxn, eh.uniform_heuristic, 1000, prob, depth))

if __name__ == "__main__":
    main()
