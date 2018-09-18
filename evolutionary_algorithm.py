from collections import namedtuple, Counter
from itertools import combinations
from copy import deepcopy
import statistics
import json
import random

CANVAS_DIMENSION = 800

Link = namedtuple('Link', ['source', 'target'])


# graph


links = [
    Link(0, 3),
    Link(3, 6),
    Link(6, 9),
    Link(0, 1),
    Link(1, 4),
    Link(4, 7),
    Link(0, 2),
    Link(2, 5),
    Link(5, 8),
    Link(9, 7),
    Link(6, 4),
    Link(3, 1),
    Link(7, 8),
    Link(4, 5),
    Link(1, 2),
    Link(2, 3),
    Link(5, 6),
    Link(8, 9)
]


'''
links = [
    Link(0, 3),
    Link(0, 1),
    Link(0, 2),
    Link(1, 2),
    Link(1, 3),
    Link(2, 3)
]
'''


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "({}, {})".format(self.x, self.y)

    def __repr__(self):
        return "({}, {})".format(self.x, self.y)


class Individual:
    def __init__(self, chromosome, fitness):
        self.chromosome = chromosome
        self.fitness = fitness

    def __str__(self):
        return "{}".format(self.fitness)

    def __repr__(self):
        return str(self.fitness)

def initialize_population(SIZE):

    population = [None] * SIZE

    for i in range(SIZE):
        chromosome = [None] * 10
        fitness = -1

        for j in range(10):
            x = random.randint(0, 800)
            y = random.randint(0, 800)
            chromosome[j] = Point(x, y)

        population[i] = Individual(chromosome, fitness)


    return population


def is_incident(l1, l2):
    return True if len(set([l1.source, l1.target, l2.source, l2.target])) == 3 else False

def compute_orientation(p, q, r):
    # compute cross product
    cp = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)

    if cp == 0:
        return 0 # collinear
    elif cp > 0:
        return 1 # clockwise
    else:
        return 2 # counterclockwise

def is_on_segment(p, q, r):
   return True if q.x <= max(p.x, r.x) and  q.x >= min(p.x, r.x) and q.y <= max(p.y, r.y) and q.y >= min(p.y, r.y) else False


def do_links_intersect(l1, l1_p, l1_q, l2, l2_p, l2_q):
    o1 = compute_orientation(l1_p, l1_q, l2_p)
    o2 = compute_orientation(l1_p, l1_q, l2_q)
    o3 = compute_orientation(l2_p, l2_q, l1_p)
    o4 = compute_orientation(l2_p, l2_q, l1_q)

    if is_incident(l1, l2):
        if o1 != o2 and o3 != o4:
            return False
        else:
            # only have 3 points to deal with, the set will remove the duplicate
            endpoints = {l1_p, l1_q, l2_p, l2_q}
            midpoint = Counter([l1_p, l1_q, l2_p, l2_q]).most_common(1)[0][0]

            for point in endpoints:
                if midpoint.x == point.x and midpoint.y == point.y:
                    endpoints.remove(point)
                    break

            ep1, ep2 = endpoints

            if is_on_segment(ep1, ep2, midpoint):
                return True

            if is_on_segment(ep2, ep1, midpoint):
                return True

            return False

    else:
        if o1 != o2 and o3 != o4:
            return True

        if o1 == 0 and is_on_segment(l1_p, l2_p, l1_q):
            return True

        if o2 == 0 and is_on_segment(l1_p, l2_q, l1_q):
            return True

        if o3 == 0 and is_on_segment(l2_p, l1_p, l2_q):
            return True

        if o4 == 0 and is_on_segment(l2_p, l1_q, l2_q):
            return True

        return False

def compute_fitness(individual):
    link_crossings = 0
    link_pairs = combinations(links, 2)
    num_link_pairs = len(list(combinations(links, 2)))

    for link_pair in link_pairs:
        if (do_links_intersect(
                link_pair[0], individual.chromosome[link_pair[0].source], individual.chromosome[link_pair[0].target],
                link_pair[1], individual.chromosome[link_pair[1].source], individual.chromosome[link_pair[1].target])):
            link_crossings += 1

    # the number of pairs of edges in the graph that don't intersect
    individual.fitness = num_link_pairs - link_crossings

def evaluate(population):

    for individual in population:
        compute_fitness(individual)

def recombination(population):

    recombination_rate = 0.5
    population_xo = [None] * len(population)

    for index, individual in enumerate(population):
        if random.random() > recombination_rate:
            offspring = individual

        else:
            offspring = individual
            parent_2_index = random.randint(0, len(population) - 1)

            parent_2 = population[parent_2_index]
            xo_point = random.randint(0, len(individual.chromosome) - 1)

            for i in range(len(offspring.chromosome)):
                if i > xo_point:
                    offspring.chromosome[i].x = parent_2.chromosome[i].x
                    offspring.chromosome[i].y = parent_2.chromosome[i].y

        population_xo[index] = offspring

    return population_xo


def mutation(population):

    mutation_rate = 0.05
    population_mut = [None] * len(population)

    for index, individual in enumerate(population):
        if random.random() > mutation_rate:
            offspring = deepcopy(individual)
        else:
            offspring = deepcopy(individual)
            locus = random.randint(0, len(individual.chromosome) - 1)
            offspring.chromosome[locus].x = random.randint(0, CANVAS_DIMENSION)
            offspring.chromosome[locus].y = random.randint(0, CANVAS_DIMENSION)

        population_mut[index] = deepcopy(offspring)

    return population_mut


def selection(population):

    population_sel = [None] * len(population)

    fitness_sum = sum([individual.fitness for individual in population])

    for index, individual in enumerate(population):
        random_stopping_point = random.randint(0, fitness_sum)
        partial_sum = 0

        for individual_x in population:
            partial_sum += individual_x.fitness

            if partial_sum >= random_stopping_point:
                population_sel[index] = deepcopy(individual_x)
                break

    return population_sel


def genetic_algorithm():

    current_generation = 0
    num_generations = 1500

    current_max_fitness = 0
    max_fitness = len(list(combinations(links, 2)))

    population = initialize_population(300)


    with open('data.json', 'w') as file:

        best_graphs = list()

        while current_generation < num_generations and current_max_fitness < max_fitness:

            population = recombination(population)
            population = mutation(population)
            evaluate(population)
            population = selection(population)

            current_max_fitness = max([individual.fitness for individual in population])
            current_min_fitness = min([individual.fitness for individual in population])
            current_mean = statistics.mean([individual.fitness for individual in population])

            print(current_generation, current_max_fitness, current_min_fitness, current_mean)

            for individual in population:
                if individual.fitness == current_max_fitness:
                    current_graph = dict()
                    current_graph['nodes'] = []
                    current_graph['links'] = []
                    current_graph['generation'] = current_generation
                    current_graph['fitness'] = current_max_fitness / max_fitness

                    for link in links:
                        current_graph['links'].append({"source": link.source, "target": link.target})

                    for index, dna in enumerate(individual.chromosome):
                        current_graph['nodes'].append({"id": index, "x": dna.x, "y": dna.y})

                    best_graphs.append(current_graph)
                    break

            current_generation += 1

        json.dump(best_graphs, file, indent=4)
        file.write('\n')


if __name__ == '__main__':
    genetic_algorithm()
















