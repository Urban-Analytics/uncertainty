""" ABC rejection sampling. """

import numpy as np
import random
from time import strftime, time
import multiprocessing as mp
from tabulate import tabulate
import pickle
import matplotlib.pyplot as plt

from sugarscape_cg.model import SugarscapeCg


run_id = '210209_134031'
obs = 66
yticks = range(1, 6)
xticks = range(1, 18)

def load_hm_results():
    """ Returns plaus space and quantified uncertainty. """
    with open('results/%s/hm.pkl' % run_id, 'rb') as pfile:
        hm_results = pickle.load(pfile)
    # return final plaus space where everything was found to be plausible
    return hm_results[-1]['plaus_space'], np.sqrt(hm_results[-1]['uncert'])


def run_simulation(x):
    SS = SugarscapeCg(max_metabolism=x[0], max_vision=x[1])
    SS.verbose = False
    y =  SS.run_model(step_count=30)
    return y


plaus_space, uncert = load_hm_results()


# set parameters, specify functions and initialise storage objects
N = 10000  # number of particles
theta = np.zeros(N)  # particle results

def abc(_):
    d = uncert + 1  # initialise d to be greater than the tolerance threshold
    attempts = 1
    while d > uncert:
        # sample from the prior
        sample = plaus_space[random.randint(0, len(plaus_space)-1)]
        x = run_simulation(sample)  # simulate data
        d = abs(obs - x)
        attempts += 1
    return sample, attempts, d  # store the accepted value


# run the algorithm
def run_it():
    a = time()
    pool = mp.Pool(mp.cpu_count())
    results = pool.map_async(abc, range(N)).get()
    pool.close()
    b = time()
    print('Total time:', round(b - a))
    return results


def plot_results(theta=None):
    if theta == None:
        with open('results/%s/abc_reject.pkl' % run_id, 'rb') as pfile:
            results = pickle.load(pfile)
            theta = [r[0] for r in results]
    fig, axes = plt.subplots(1, 1, figsize=(9, 3))
    # are weight necessary?
    W = [1 for i in range(N)]
    X = [t[1] for t in theta]
    Y = [t[0] for t in theta]
    p = plt.hist2d(x=X, y=Y, weights=W, density=True,
                   bins=((xticks, yticks)), cmap='magma')
    plt.xlabel('max vision')
    plt.ylabel('max metabolism')
    plt.xticks([x+0.5 for x in xticks[:-1]], xticks[:-1])
    plt.yticks([y+0.5 for y in yticks[:-1]], yticks[:-1])
    plt.colorbar(p[3])
    fig.tight_layout()
    #plt.show()
    plt.savefig('results/%s/abc_reject_results.pdf' % run_id)


# results = run_it()
# with open('results/%s/abc_reject.pkl' % run_id, 'wb') as pfile:
#         hm_results = pickle.dump(results, pfile)
#
# theta = [r[0] for r in results]
# total_attempts = sum([r[1] for r in results])
# print('Total attempts:', total_attempts)
# plot_results(theta)
plot_results()
