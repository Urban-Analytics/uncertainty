""" Run tests of using HM and ABC rejection sampling on the hoopoes model.

1. Sample lots of parameters in the sample space.
2. For each sample, generate some observations.
3. Perform history matching (HM) on the sample space
   to find the parameters that match the observations.
4. Run ABC rejection sampling using the non-implausible
   space found through HM as an informed prior.
5. Run ABC rejection sampling using an uninformed prior.
6. Compare the results and total model runs required when
   using HM compared with not using HM.

"""


import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
import pandas as pd
from scipy import spatial

import hoopoes_hm as hhm
import hoopoes_abc_reject as abcreject
import helper


params = helper.params
result = helper.result

SAMPLES = 100
DIMENSIONS = 2
PARAMETERS = ['scout_prob', 'survival_prob']
OUTPUTS = ['abundance', 'variation', 'vacancies']
ORIG_BOUNDS = {'scout_prob': (0, 0.5),
               'survival_prob': (0.95, 1)}

try:
    with open('observations.pkl', 'rb') as pfile:
        observations = pickle.load(pfile)
except FileNotFoundError:
    raise Exception('No observations found. Run get_observations()')


def get_observations():
    """ Sample the parameter space and get observations for each sample. """
    hhm.samples = SAMPLES
    X = hhm.init_sampparams = pd.DataFrame([(r.scout_prob, r.survival_prob) for r in results],
                                   columns=('scout prob', 'survival prob'))
    X = [(round(x[0], ROUNDING), round(x[1], ROUNDING)) for x in X]
    results = np.empty(SAMPLES, dtype=object)
    # Get 10 observations so we have some observation uncertainty
    obs = pyrun.run_ensembles(X, 10)
    index = 0
    for x in X:
        scout, survival = x
        # The filename indicates the parameters used to get the observations.
        dir = 'results/run_%d_%d' % (int(scout*10**ROUNDING), int(survival*10**ROUNDING))
        r = result(params(scout, survival), obs[index], dir)
        results[index] = r
        index += 1
    print(results)  # In case saving goes wrong.
    with open('observations.pkl', 'wb') as pfile:
        pickle.dump(results, pfile)


def run_HM():
    """ Run history matching against the store list of observations."""
    index = 0
    for obs in observations:
        print('index %d' % index)
        # if the directory already exists, then we already have results
        if not os.path.isdir(obs.results_dir):
            for output_i in range(3):
                output_Y = [y[output_i] for y in obs.obs]
                hhm.pyrun.criteria[OUTPUTS[output_i]] = (min(output_Y), max(output_Y))
            hhm.run_waves(obs.results_dir)
        index += 1


def analyse_HM_obs(obs):
    """ Analyse the HM results. """
    empty, failed = 0, 0
    cum_space_decrease = np.zeros(2)
    if os.path.isdir(obs.results_dir):  # check there are results
        accepted_space = helper.last_wave(obs.results_dir)
        if len(accepted_space) == 0:
            #print(obs.results_dir, 'Empty plausible space.')
            empty = 1
        else:
            target = helper.split(obs.parameters)
            bounds = helper.get_bounds(accepted_space)
            for d in range(DIMENSIONS):
                cum_space_decrease[d] = \
                        (helper.bound_len(bounds[PARAMETERS[d]]) /
                         helper.bound_len(ORIG_BOUNDS[PARAMETERS[d]]))
                if not helper.in_bound(target[d], bounds[PARAMETERS[d]]):
                    failed = 1
                    #print(obs.results_dir, 'Target parameter discarded')
    return empty, failed, cum_space_decrease




def run_abc_reject():
    for obs in observations[33:]:
        print(obs.parameters)
        accepted_space = helper.last_wave(obs.results_dir)
        if (len(accepted_space) > 0  # there are HM results
                and not os.path.exists('%s/abc_history.pkl' % obs.results_dir)): # but no abc results already
            # Set the expected output
            for output_i in range(3):
                output_Y = [y[output_i] for y in obs.obs]
            # Set the priors
            bounds = helper.get_bounds(accepted_space)
            abcreject.pyrun.criteria[OUTPUTS[output_i]] = (min(output_Y), max(output_Y))
            abcreject.threshold = 1
            # Run with HM prior
            abcreject.scout_prob_range = bounds['scout_prob']
            abcreject.survival_prob_range = bounds['survival_prob']
            abcreject.go(obs.results_dir, '_hm')
            # # Run without HM prior
            abcreject.scout_prob_range=(0, 0.5)
            abcreject.survival_prob_range=(0.95, 1)
            abcreject.go(obs.results_dir)


def abc_reject_analyse(obs):
    """ Check if ABC failed to retain the correct parameter without and with HM prior."""
    failure_results = [1, 1]
    suffixes = ('', '_hm')
    if (os.path.exists('%s/abc_reject.pkl' % obs.results_dir) and
                os.path.exists('%s/abc_reject_hm.pkl' % obs.results_dir)):
        for test in range(2):
            with open('%s/abc_reject%s.pkl' % (obs.results_dir, suffixes[test]), 'rb') as pfile:
                results = pickle.load(pfile)
            params = pd.DataFrame([(r.scout_prob, r.survival_prob) for r in results],
                                   columns=('scout prob', 'survival prob'))
            tree = spatial.KDTree(params)
            idx = tree.query((obs.parameters.scout_prob, obs.parameters.survival_prob))[1]
            if results[idx].error > 0.5:
                failure_results[test] = 0
    return failure_results

def analyse():
    hm_total_failures = 0
    hm_total_empties = 0
    hm_cum_space_decrease = np.zeros(2)
    abc_total_failures = 0
    abc_with_hm_total_failures = 0
    for obs in observations:
        empty, failed, cum_space = analyse_HM_obs(obs)
        hm_total_empties += empty
        hm_total_failures += failed
        hm_cum_space_decrease += cum_space
        if empty == 0 and failed == 0:
            without_hm, with_hm = abc_reject_analyse(obs)
            abc_total_failures += without_hm
            abc_with_hm_total_failures += with_hm

    print('HM results:')
    print('Total where target parameter was discarded: %d' % hm_total_failures)
    print('Total empty plausible spaces: %d' % hm_total_empties)
    print('Average space decrease for %s: %d' % (PARAMETERS[0], hm_cum_space_decrease[0]))
    print('Average space decrease for %s: %d' % (PARAMETERS[1], hm_cum_space_decrease[1]))
    print('\nABC results:')
    print('Total where target parameter was discarded without HM prior: %d' % abc_total_failures)
    print('Total where target parameter was discarded with HM prior: %d' % abc_with_hm_total_failures)


def compare_runs():
    def total_runs(dir, suffix):
        with open('%s/abc_reject%s.pkl' % (dir, suffix), 'rb') as pfile:
            results = pickle.load(pfile)
        return sum(r.attempts for r in results)
    runs_with_hm = []
    runs_without_hm = []
    saves = []
    for obs in observations:
        if (os.path.exists('%s/abc_reject.pkl' % obs.results_dir) and
                    os.path.exists('%s/abc_reject_hm.pkl' % obs.results_dir)):
            runs_with_hm.append(total_runs(obs.results_dir, '_hm'))
            runs_without_hm.append(total_runs(obs.results_dir, ''))
            saves.append(runs_without_hm[-1] - runs_with_hm[-1])
    print('Average ABC runs with informed prior:', np.mean(runs_with_hm))
    print('Average ABC runs without informed prior:', np.mean(runs_without_hm))
    #print(np.mean(saves))
    print('Averaged saved by using HM:',
          np.mean(np.array(saves) - np.array(helper.hm_total_runs(observations))))


def abc_reject_plot():
    for obs in observations:
        dir = obs.results_dir
        if (os.path.exists('%s/abc_reject.pkl' % obs.results_dir) and
                    os.path.exists('%s/abc_reject_hm.pkl' % obs.results_dir)):
            abcreject.plot_results(dir, suffix='')
            abcreject.plot_results(dir, suffix='_hm')



if __name__ == '__main__':
    #run_HM()
    analyse()
    #run_abc_reject()
    #abc_reject_analyse(observations[0])
    #abc_reject_plot()
