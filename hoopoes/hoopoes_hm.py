import numpy as np
import lhsmdu
import csv
import pickle
import matplotlib.pyplot as plt
from time import strftime
import os, sys

import pyrun

# import history_matching from parent directory
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import history_matching


DIMENSIONS = 2
PARAMETERS = ['scout_prob', 'survival_prob']
# bounds are same as those given in the paper
bounds = {'scout_prob': (0, 0.5),
          'survival_prob': (0.95, 1)}

history_matching.sim_func = pyrun.run_simulation
history_matching.error_func = pyrun.error
# Parallel processing must be done within pyrun not history_matching
# (pynetlogo is fussy about this),
# so tell history_matching where those functions are.
history_matching.ensemble_func = pyrun.run_ensembles
history_matching.variety_func = pyrun.run_varieties
# We're excluding model discrepancy as it causes the uncertainty to be too high,
# resulting in almost the whole sample space being accepted.
history_matching.include_model_disc = False

history_matching.k = 30  # runs in an ensemble, change as desired
samples = 50  # change as desired

results = []


def bind_list(X, limits):
    """ Scale values in a list so the smallest and largest values
        are the same as the provided limits."""
    return X * (bounds[limits][1] - bounds[limits][0]) + bounds[limits][0]


def bind_value(x, limits):
    """ Bring a single within the limits if it has fallen outside."""
    x = max(bounds[limits][0], x)
    x = min(bounds[limits][1], x)
    return x


# NOTE: Alternative resampling method
# ~ def perturb(X):
    # ~ """ Perturb each dimension of values by 20% of their std dev."""
    # ~ for d in range(DIMENSIONS):
        # ~ lst = [x[d] for x in X]
        # ~ p = np.std(lst) * 0.2
        # ~ new_lst = [bind_value(a + ((np.random.random() * p * 2) - p),
                              # ~ PARAMETERS[d])
                   # ~ for a in lst]
        # ~ for i in range(len(X)):
            # ~ X[i][d] = new_lst[i]
    # ~ return X


def resample(X):
    """ Resample X within the mean and 1.2*std of the plausible samples."""
    new_X = np.zeros((samples, DIMENSIONS))
    for d in range(DIMENSIONS):
        lst = [x[d] for x in X]
        p = np.std(lst) * 1.2
        m = np.mean(lst)
        new_lst = np.random.normal(m, p, samples)
        for i in range(samples):
            # the random sample may be outside of the accepted bounds
            new_X[i][d] = bind_value(new_lst[i], PARAMETERS[d])
    return new_X.tolist()


def save_results(results_dir):
    """ Save results of all waves using pickle. """
    # overwrites save of the previous wave
    filepath = '%s/hm.pkl' % results_dir
    with open(filepath, 'wb') as pfile:
        pickle.dump(results, pfile)


def plot_wave(wave, show=True):
    plt.clf()
    for ps in range(len(wave['plaus_space'])):
        if wave['implaus_scores'][ps] < 3:
            plt.scatter((wave['plaus_space'][ps][0],),
                        (wave['plaus_space'][ps][1],),
                        c='sandybrown')
        else:
            plt.scatter((wave['plaus_space'][ps][0],),
                        (wave['plaus_space'][ps][1],),
                         c='dimgrey')
    plt.xlim(bounds['scout_prob'][0]-0.005, bounds['scout_prob'][1]+0.005)
    plt.ylim(bounds['survival_prob'][0]-0.005, bounds['survival_prob'][1]+0.005)
    plt.xlabel('scouting probability')
    plt.ylabel('survival probability')
    if show:
        plt.show()


def plot_saved_results(results_dir, save=False):
    with open('results/%s/hm.pkl' % results_dir, 'rb') as pfile:
        results = pickle.load(pfile)
    for wave in results:
        if save:
            plot_wave(wave, show=False)
            plt.savefig('results/%s/wave_%d.pdf' % (results_dir, wave['wave_no']))
        else:
            plot_wave(wave, show=True)


def init_sample():
    """ Use LHS design to create samples for the first wave. """
    X = lhsmdu.sample(DIMENSIONS, samples)
    X[0] = bind_list(X[0], 'scout_prob')
    X[1] = bind_list(X[1], 'survival_prob')
    X = X.T
    X = X.tolist()
    return X


def has_plaus_space_decreased():
    """ Measure if the area of the latest plausible space
        is smaller than the previous.

        Information on the plausible space is taken from the variable 'results'.
        Returns: Boolean
    """
    def area(wave):
        d0 = []
        d1 = []
        for i in range(len(wave['implaus_scores'])):
            if wave['implaus_scores'][i] < 3:
                d0.append(wave['plaus_space'][i][0])
                d1.append(wave['plaus_space'][i][1])
        return (max(d0) - min(d0)) * (max(d1) - min(d1))
    try:
        latest_area = area(results[-1])
        previous_area = area(results[-2])
        return latest_area < previous_area
    except IndexError:
        # Need at least 2 waves to test if the space has decreased.
        # Report True until test is possible
        return True


def run_waves():
    results_dir = 'results/%s' % strftime('%y%m%d_%H%M%S')
    os.mkdir(results_dir)
    wave_no = 1
    new_plaus_space = init_sample()
    plaus_space = []
    # stop if the plausible space has not narrowed any smaller
    # or if only one or no samples are plausible
    #while len(new_plaus_space) > 1 and has_plaus_space_decreased():
    while wave_no < 7:
        plaus_space = new_plaus_space
        if wave_no > 1:
            # Explore around the plausible space found,
            # rather than retesting the same samples as the previous wave
            plaus_space = resample(plaus_space)
        uncert, new_plaus_space, implaus_scores = history_matching.wave(plaus_space)
        results.append({'wave_no': wave_no,
                        'uncert': uncert,
                        'plaus_space': plaus_space,
                        'implaus_scores': implaus_scores})
        wave_no += 1
        print(len(new_plaus_space))
        #plot_wave(results[-1])
        # save results at each iteration so they can be examined during runtime
        save_results(results_dir)


if __name__ == '__main__':
    #run_waves()
    #plot_saved_results('210125_151327', save=False)
    plot_saved_results('210209_100055', save=False)
