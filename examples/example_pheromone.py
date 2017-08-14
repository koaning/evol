"""
python examples/example_pheromone.py
python examples/example_pheromone.py --population-size=35 --num-iter=1000
python examples/example_pheromone.py --population-size=100 --num-iter=1000
"""

import random
import math
import fire
import itertools as it
import matplotlib.pylab as plt

from evol import Population


def run_pheromone(num_towns=21, population_size=20, num_iter=200, seed=42):
    """Runs a pheromone tactic against a simple TSP."""
    num_towns = num_towns
    coordinates = [(random.random(), random.random()) for i in range(num_towns)]
    random.seed(seed)

    pheromones = {arc:1 for arc in it.product(range(num_towns), range(num_towns)) if arc[0] != arc[1]}

    def init_func():
        order = list(range(num_towns))
        random.shuffle(order)
        return order

    def eval_func(order):
        return sum([dist(coordinates[order[i]], coordinates[order[i - 1]]) for i, t in enumerate(order)])

    def dist(t1, t2):
        return math.sqrt((t1[0] - t2[0]) ** 2 + (t1[1] - t2[1]) ** 2)

    def sliding_window(iter):
        for i in range(len(iter) - 1):
            yield iter[i], iter[i+1]

    def update_pheromones(chromosome):
        for gene1, gene2 in sliding_window(chromosome):
            pheromones[(gene1, gene2)] += 1
            pheromones[(gene2, gene1)] += 1

    def combiner(parent):
        order = [0]
        for town in range(num_towns-1):
            next_dict = {towns[1]: val for towns,val in pheromones.items()
                         if (towns[1] not in order) and (towns[0] == order[-1])}
            next_town = random.choices(population=list(next_dict.keys()),
                                       weights=list(next_dict.values()))
            order.append(next_town[0])
        return order


    pop = Population(init_function=init_func,
                     eval_function=eval_func,
                     size=population_size, maximize=False).evaluate()
    scores = []
    iterations = []
    for iter in range(num_iter):
        print(f"iteration: {iter} best score: {min([individual.fitness for individual in pop])}")
        for indiviual in pop:
            scores.append(indiviual.fitness)
            iterations.append(iter)
        pop.survive(fraction=0.2)
        for indiviual in pop:
            update_pheromones(indiviual.chromosome)
        pop.survive(n=1)
        pop.breed(parent_picker=lambda x: random.choice(x), combiner=combiner).evaluate()

    plt.scatter(iterations, scores, s=1, alpha=0.3)
    plt.title("population fitness vs. iteration")
    plt.show()

if __name__ == "__main__":
    fire.Fire(run_pheromone)