""" Run history matching and approximate bayesian computation
    to explore the parameter max_metabolism in Sugarscape.
"""    


import numpy as np
import random
from time import strftime, time
import multiprocessing as mp
from tabulate import tabulate

from sugarscape_cg.model import SugarscapeCg
import history_matching
import sugarscape_hm


def run_simulation(x):
    SS = SugarscapeCg(initial_population=100, max_metabolism=x)
    SS.verbose = False
    # The model is simple enough that 30 steps is
    # sufficient to reach a steady population state.
    y =  SS.run_model(step_count=30)
    return y  # total number of agents remaining in the simulation


def run_history_matching(new_plaus_space):
    plaus_space = []  # not yet explored
    while not history_matching.is_all_plausible(plaus_space, new_plaus_space):
        plaus_space = new_plaus_space
        new_plaus_space, implaus_scores, v_ens = history_matching.wave(plaus_space)
        sugarscape_hm.plot_implaus_1d(plaus_space, implaus_scores)
    print('Finished with', str(new_plaus_space))
    return new_plaus_space, v_ens


obs = run_simulation(4)
print('observation:', obs)
history_matching.y = obs  # the real world observation
history_matching.f = run_simulation  # the function (simulation) used for history matching


# initial plausible space to explore
# note that SugarscapeCg only takes integer values for metabolism
plaus_space = np.array(range(1, 5))
plaus_space, uncert = run_history_matching(plaus_space)


N = 1  # number of particles
theta = np.zeros(N)  # particle results
rho = lambda x,y: abs(x-y)  # measure of error


def abc(_):
    d = uncert + 1  # initialise d to be greater than the tolerance threshold
    while d > uncert:
        # sample from the prior
        sample = plaus_space[random.randint(0, len(plaus_space)-1)] 
        x = run_simulation(sample)  # simulate data
        d = rho(obs, x)  # compute distance
    return sample  # store the accepted value


# run the algorithm
a = time()
pool = mp.Pool(mp.cpu_count())
theta = pool.map_async(abc, range(N)).get()
pool.close()
b = time()


# print results
print('Time taken (s):', str(round(b - a)))
print('Results:')
table = []
for x in plaus_space:
    table.append([x, theta.count(x)])
print(tabulate(table, headers=['parameter', 'posterior']))
