""" Run ABC rejection sampling on the Hoopoes model. """

import numpy as np
import pandas as pd
import random
from time import strftime, time
from typing import NamedTuple
import multiprocessing as mp
from tabulate import tabulate
import pickle
import matplotlib.pyplot as plt
import pyabc  # for plotting

import helper
import pyrun

# Number of particles.
N = 1000

# Default uninformed priors.
scout_prob_range=(0, 0.5)
survival_prob_range=(0.95, 1)

# To determine if a result is kept.
threshold = 1


class result(NamedTuple):
    particle_id: int
    scout_prob: float
    survival_prob: float
    attempts: int  # Total attempted parameters tested.
    error: float  # Error of the accepted model run.
    seconds: int  # Total time taken for all attempts.


def abc(particle_no):
    """ Run rejection sampling for one particle. """
    d = threshold + 1  # Initialise d to start the while loop.
    attempts = 0
    start_time = time()
    np.random.seed(int(start_time/(particle_no+1)))
    while d > threshold:
        # Sample from the prior.
        scout = np.random.random() * (scout_prob_range[1] - scout_prob_range[0]) + scout_prob_range[0]
        survival = np.random.random() * (survival_prob_range[1] - survival_prob_range[0]) + survival_prob_range[0]
        y = pyrun.run_solo((scout, survival))  # Simulate data.
        d = pyrun.error(y)
        attempts += 1
    end_time = time()
    return result(particle_no, scout, survival, attempts, d, round(end_time-start_time))



def go(run_id, suffix=''):
    """ Run rejection sampling for all particles and save the results. """
    pool = mp.Pool(mp.cpu_count())
    results = pool.map_async(abc, range(N)).get()
    pool.close()
    with open('%s/abc_reject%s.pkl' % (run_id, suffix), 'wb') as pfile:
        pickle.dump(results, pfile)
    total_attempts = sum([r.attempts for r in results])
    print('Total attempts:', total_attempts)


def plot_results(run_id, suffix=''):
    with open('%s/abc_reject%s.pkl' % (run_id, suffix), 'rb') as pfile:
        results = pickle.load(pfile)
    params = pd.DataFrame([(r.scout_prob, r.survival_prob) for r in results],
                           columns=('scout prob', 'survival prob'))
    w = np.ones(N)
    # Plot the posterior
    fig, ax = plt.subplots()
    pyabc.visualization.plot_kde_2d(
        params, w, x="scout prob", y="survival prob",
        xmin=0, xmax=0.5, ymin=0.95, ymax=1,
        ax=ax, cmap='magma')
    plt.xlabel('scouting probability', fontsize=16)
    plt.ylabel('survival probability', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    fig.subplots_adjust(bottom=0.15)
    #plt.show()
    plt.savefig('%s/abc_posterior%s.eps' % (run_id, suffix))
    plt.close()


if __name__ == '__main__':
    # id gives directory of results replicating Theile et al.
    id = 'results/210125_151327'
    # Run with uninformed prior
    go(id)
    plot_results(id)
    # Get HM results
    accepted_space = helper.last_wave(id)
    bounds = helper.get_bounds(accepted_space)
    # Run with HM-informed prior
    scout_prob_range = bounds['scout_prob']
    survival_prob_range = bounds['survival_prob']
    go(id, '_hm')
    plot_results(id, '_hm')
