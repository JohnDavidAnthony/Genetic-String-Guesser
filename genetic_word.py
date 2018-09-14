import random
import math
import time
from time import sleep
import numpy as np
from argparse import ArgumentParser


# Creates a list of random combinations of the gene_set
def generate_inital(length, pop_size, gene_set):
    inital_pop = []
    for _ in range(pop_size):
        genome = ""
        for _ in range(length):
            genome += random.choice(gene_set)
        inital_pop.append(genome)
    return inital_pop

# Fitness function based on how close the guess is to the target worked
def fitness(target, guess):
    score = 0
    for index in range(len(target)):
        if (target[index] == guess[index]):
            score += 1
    return score

# Breed more children by combing genes of both parents
def breed(parent1, parent2):
    l_parent1 = list(parent1)
    l_parent2 = list(parent2)
    
    for index in range(len(parent1)):
        if random.randint(0,1) == 1:
            temp = l_parent1[index]
            l_parent1[index] = l_parent2[index]
            l_parent2[index] = temp
    return ["".join(l_parent1), "".join(l_parent2)]

# Mutate the genome by editing some of its genes based on the mutation rate
def mutate(child, rate, gene_set):
    l_child = list(child)
    if random.randint(0,rate-1) == 0:
        for _ in range(random.randint(0, round((len(l_child)-1)/4))):
            index = random.randint(0, len(l_child)-1)
            gene = random.choice(gene_set)
            l_child[index] = gene
    return "".join(l_child)

# Gets the fitness of each genome and sorts descending by fitness
def sort_fitness(target, population):
    population_fitness = []

    for guess in population:
        fit = fitness(target, guess)
        population_fitness.append([guess, fit])
    
    x = sorted(population_fitness, key = lambda x: int(x[1]))
    x.reverse()
    
    return x

# Make room for the new generation by more likely killing the worst genomes 
def kill(sorted_popualtion, new_pop_size):
    # Save the best 
    best = round(len(sorted_popualtion) * .2)
    new_pop = sorted_popualtion[: best]
    sorted_popualtion = sorted_popualtion[best:]
    # Randomly Select others to keep, biased for those who were more fit
    while(len(new_pop) < new_pop_size):
        saved_index = math.floor(math.fabs(random.random() - random.random()) * (len(sorted_popualtion) - 0) + 0)
        # print ("saved_index {0} length of new_pop {1}".format(saved_index, len(sorted_popualtion)))
        new_pop.append(sorted_popualtion.pop(saved_index))

    return new_pop

# Get the next generation by breeding and mutating
def regeneration(new_population, pop_size, mutation_rate, gene_set):
    next_gen = []
    while (len(new_population) + len(next_gen)) < pop_size:
        mate1 = ""
        mate2 = ""
        while mate1 == mate2:
            mate1 = math.floor(math.fabs(random.random() - random.random()) * (len(new_population) - 0) + 0)
            mate2 = math.floor(math.fabs(random.random() - random.random()) * (len(new_population) - 0) + 0)
    
        child1, child2 = breed(new_population[mate1][0], new_population[mate2][0])
        next_gen.append(child1)
        next_gen.append(child2)

    for genome in new_population:
        next_gen.append(genome[0])

    # Mutate
    for index in range(len(next_gen)):
        next_gen[index] = mutate(next_gen[index], mutation_rate, gene_set)

    return next_gen

# Returns the fitness of all genomes
def stats(population):
    stat_list = []
    for genome in population:
        stat_list.append(genome[1])
    
    return stat_list

def genetic_guess(target, pop_size, gene_set, mutation_rate, feedback=False, reporting_rate=10):
    sleep_time = .01
    start = time.time()

    # Get Inital Population
    inital = generate_inital(len(target), pop_size, gene_set)
    # Sort the Inital Pop by fitness
    sorted_gen = sort_fitness(target, inital)

    if feedback:
        print ("Inital Population:\n\n")
        for guess in sorted_gen:
            print ("{0}: {1}".format(guess[0], guess[1]))
        sleep(sleep_time)

    prev_std = np.std(np.array(stats(sorted_gen)))
    new_std = -1

    generation_num = 1
    while(abs(new_std - prev_std) > .0001 ):
        # Get the new Population after we kill off the worst
        new_pop = kill(sorted_gen, pop_size * .5)
        # Breed and mutate what is left of the prev generation
        next_gen = regeneration(new_pop, pop_size, mutation_rate, gene_set)

        # Sory the Population by fitness
        sorted_gen = sort_fitness(target, next_gen)
        if feedback and generation_num % reporting_rate == 0:
            print("\n Generation {0}".format(generation_num))
            print ("{0}: {1}".format(sorted_gen[0][0], sorted_gen[0][1]))

            print(np.std(np.array(stats(sorted_gen))))
            sleep(sleep_time)

        if sorted_gen[0][1] == len(target):
            finish = time.time()
            print("\nSuccessfully found: {0} after {1} Generations with a population size of {2} in {3} seconds!".format(target, generation_num, pop_size, round(finish-start)))
            exit(0)


        generation_num += 1

    print ("Unable to find {0}.".format(target))

# Argument Parser for CLI
parser = ArgumentParser()
parser.add_argument("-t", "--target",
                    default="This is an example of string for the genetic algorithm to guess.",
                    type=str,
                    help="Str: The string for the genetic algorithm to guess")

parser.add_argument("-l", "--library",
                    default=" abcdefghijklmnopqrstuv{0}wxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!.,'1234567890`-=_+[]!@#$%^&*()<>?/\|`~".format('"}{'),
                    type=str,
                    help="Str: All possible chars that could be in the target, default are the alphanumeric chars")

parser.add_argument("-p", "--population",
                    default=1000,
                    type=int,
                    help="Int: The number of genomes in each generation")

parser.add_argument("-m", "--mutate",
                    default=2,
                    type=int,
                    help="Int: The mutation rate, i.e if you put 2, 1:2 mutation to no mutation")

parser.add_argument("-f", "--feedback",
                    default=True,
                    type=bool,
                    help="Bool: If you want feedback on the progress of the algoithm.")

parser.add_argument("-r", "--reporting",
                    default=10,
                    type=int,
                    help="Int: How often you want reports if --feedback is set, every x generations")        
args = parser.parse_args()

genetic_guess(args.target, args.population, args.library, args.mutate, args.feedback, args.reporting)
