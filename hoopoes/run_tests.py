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
from matplotlib.colors import Normalize
from shapely.geometry import Polygon, Point
import pandas as pd
from scipy import spatial
import pyabc
from tabulate import tabulate

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
    """ Run history matching against the stored list of observations."""
    index = 0
    for obs in observations:
        print('index %d' % index)  # print index to keep track of progress
        # If the directory exists, then we already have results.
        # This is useful if we stopped midway through running the tests.
        if not os.path.isdir(obs.results_dir):
            for output_i in range(3):
                output_Y = [y[output_i] for y in obs.obs]
                hhm.pyrun.criteria[OUTPUTS[output_i]] = (min(output_Y), max(output_Y))
            hhm.run_waves(obs.results_dir)
        index += 1


def analyse_HM_obs(obs):
    """ Analyse the HM results.
        Returns information on
        1) how many times no plausible paramters were found (the plausible space is empty)
        2) how many times the found plausible space does not contain the target parameter
        3) how much the plausible space of each parameter decreased compared to the prior.
    """
    empty, failed = 0, 0
    cum_space_decrease = np.zeros(2)
    if os.path.isdir(obs.results_dir):  # check there are results
        accepted_space = helper.last_wave(obs.results_dir)
        if len(accepted_space) == 0:
            # HM didn't find any plausible parameters
            empty = 1
        else:
            target = helper.split(obs.parameters)
            # Get the lower and upper bound of the space found to be plausible for both parameters
            bounds = helper.get_bounds(accepted_space)
            for d in range(DIMENSIONS):
                # Calculate how much the final plausible space has decreased
                # in comparison to the prior (ORIG_BOUNDS).
                cum_space_decrease[d] = \
                        (helper.bound_len(bounds[PARAMETERS[d]]) /
                         helper.bound_len(ORIG_BOUNDS[PARAMETERS[d]]))
                # Check if the observation lies within the found plausible space.
                if not helper.in_bound(target[d], bounds[PARAMETERS[d]]):
                    failed = 1
                    print(PARAMETERS[d], target[d], bounds[PARAMETERS[d]])
                    #print(obs.results_dir, 'Target parameter discarded')
    return empty, failed, cum_space_decrease




def run_abc_reject():
    """ Run ABC rejection sampling using
        1) HM results as an informed prior, and
        2) an uninformed prior.
        The results are stored in pickle files.
    """
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
    """ Check if ABC failed to give the correct parameter a probability of at least 0.5.
        This is tested both with and without the HM prior."""
    def closest(lst, K):
        lst = np.asarray(lst)
        idx = (np.abs(lst - K)).argmin()
        return idx
    failure_results = [1, 1]
    suffixes = ('', '_hm')
    w = np.ones(1000)
    if (os.path.exists('%s/abc_reject.pkl' % obs.results_dir) and
                os.path.exists('%s/abc_reject_hm.pkl' % obs.results_dir)):
        for test in range(2):
            with open('%s/abc_reject%s.pkl' % (obs.results_dir, suffixes[test]), 'rb') as pfile:
                results = pickle.load(pfile)
            params = pd.DataFrame([(r.scout_prob, r.survival_prob) for r in results],
                                   columns=('scout prob', 'survival prob'))
            X, Y, PDF = pyabc.visualization.kde.kde_2d(params, w, x="scout prob", y="survival prob")
            x_idx = closest(X[0], obs.parameters.scout_prob)
            y_idx = closest([y[0] for y in Y], obs.parameters.survival_prob)
            posterior = PDF[y_idx][x_idx]
            ratio = posterior / np.amax(PDF)
            if ratio > 0.5:
                failure_results[test] = 0
    return failure_results


def analyse():
    """ Print information on results of HM and ABC (with and without HM prior)."""
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
    print('Total tests where target parameter was discarded: %d' % hm_total_failures)
    print('Total tests resulting in an empty plausible space: %d' % hm_total_empties)
    print('Average plausible space decrease for %s: %d' % (PARAMETERS[0], hm_cum_space_decrease[0]))
    print('Average plausible space decrease for %s: %d' % (PARAMETERS[1], hm_cum_space_decrease[1]))
    print('\nABC results:')
    print('Total tests where the target parameter was discarded without HM prior: %d' % abc_total_failures)
    print('Total tests where the target parameter was discarded with HM prior: %d' % abc_with_hm_total_failures)


def compare_runs():
    """ Calculate the average number of model runs used to perform
        1) ABC with the HM-informed prior,
        2) ABC with an uninformed prior,
        and calculate the average number of runs saved by performing HM before ABC.
        """
    def total_runs(dir, suffix):
        with open('%s/abc_reject%s.pkl' % (dir, suffix), 'rb') as pfile:
            results = pickle.load(pfile)
        return sum(r.attempts for r in results)
    runs_with_hm = []
    runs_without_hm = []
    saves = []
    hm_runs = helper.hm_total_runs(observations)
    for obs_i in reversed(range(len(observations))):
        obs = observations[obs_i]
        if (os.path.exists('%s/abc_reject.pkl' % obs.results_dir) and
                    os.path.exists('%s/abc_reject_hm.pkl' % obs.results_dir)):
            runs_with_hm.append(total_runs(obs.results_dir, '_hm'))
            runs_without_hm.append(total_runs(obs.results_dir, ''))
            saves.append(runs_without_hm[-1] - runs_with_hm[-1])
        else:
            hm_runs.pop(obs_i)
    print('Average ABC runs with informed prior:', np.mean(runs_with_hm))
    print('Average ABC runs without informed prior:', np.mean(runs_without_hm))
    print('Average ABC runs saved by using informed prior:', np.mean(saves))
    print('Averaged total saved by using HM:',
          np.mean(np.array(saves) - np.array(hm_runs)))


def abc_reject_plot():
    """ Create KDE plots of the ABC results both with and without HM prior.
        Results are saved to file.
    """
    for obs in observations:
        dir = obs.results_dir
        if (os.path.exists('%s/abc_reject.pkl' % obs.results_dir) and
                    os.path.exists('%s/abc_reject_hm.pkl' % obs.results_dir)):
            abcreject.plot_results(dir, suffix='')
            abcreject.plot_results(dir, suffix='_hm')



def save_intervals():
    """ Create a csv with the columns
        run_id, hm(logical), parameter_name, real, low, high.
    """
    def check_intervals(real_survival_prob, real_scout_prob, run_id):
        """ Get the four csv lines for the given run_id.
            One line per parameter and each parameter has
            one line for HM set as True or False.
        """
        csv_lines = ""
        real_values = {"survival_prob": real_survival_prob,
                       "scout_prob": real_scout_prob}
        for suffix in ["", "_hm"]:
            with open('%s/abc_reject%s.pkl' % (run_id, suffix), 'rb') as pfile:
                results = pickle.load(pfile)
                params = pd.DataFrame([(r.scout_prob, r.survival_prob) for r in results],
                                      columns=helper.PARAMETERS)
                for parameter_name in helper.PARAMETERS:
                    high = params[parameter_name].quantile(q=0.975)
                    low = params[parameter_name].quantile(q=0.025)
                    median = params[parameter_name].quantile(q=0.5)
                    csv_lines = csv_lines + "{0},{1},{2},{3},{4},{5},{6}\n".format(
                                    str(run_id),
                                    str(suffix == "_hm"),
                                    parameter_name,
                                    str(real_values[parameter_name]),
                                    str(low),
                                    str(high),
                                    str(median))
        return csv_lines
    print("run_id,hm,parameter_name,real,low,high,median",
          file=open("confidence_intervals.csv", "w"))
    for obs in observations:
        # Check there are HM results for this run
        if (os.path.exists('%s/abc_reject.pkl' % obs.results_dir) and
                os.path.exists('%s/abc_reject_hm.pkl' % obs.results_dir)):
            print(check_intervals(obs.parameters.survival_prob,
                                  obs.parameters.scout_prob,
                                  obs.results_dir),
                  end="",
                  file=open("confidence_intervals.csv", "a"))



def analyse_intervals():
    """ Create a table showing information on
        1) how often the 95% confidence intervals contain the true paramters,
        2) the mean absolute error from calibration,
        3) the size of the 95% confidence intervals,
        for both ABC alone and HM+ABC.
    """
    table = [['ABC scout prob', None, None, None],
             ['ABC survival prob', None, None, None],
             ['ABC+HM scout prob', None, None, None],
             ['ABC+HM survival prob', None, None, None]]
    total_tests = 91  # The total tests out of 100 where HM could be performed
    results = pd.read_csv('confidence_intervals.csv')
    rowi = 0
    for hm_or_not in (False, True):
        for param in helper.PARAMETERS:
            cf_intervals = results.query("hm == %s and \
                                         parameter_name == '%s'" % (hm_or_not, param))[['real', 'low', 'high', 'median']]
            # Get MAE
            table[rowi][2] = abs(cf_intervals['real'] - cf_intervals['median']).mean()
            # Get size of 95% CI
            table[rowi][3] = round((cf_intervals['high'] - cf_intervals['low']).mean(), 3)
            # Narrow down results to those where the expected parameter is in the CI
            cf_intervals = cf_intervals.query("low <= real and real <= high")
            # Find out how many results are left compared to the total tests run.
            table[rowi][1] = round(cf_intervals.shape[0] / total_tests * 100, 2)
            rowi += 1
    print(tabulate(table, headers=('', 'Contained within 95\% CI', 'Mean Absolute Error', 'Size of 95\% CI')))




if __name__ == '__main__':
    #run_HM()
    #analyse()
    #run_abc_reject()
    #abc_reject_analyse(observations[0])
    #abc_reject_plot()
    compare_runs()
    #analyse_intervals()
    # for obs in observations:
    #     analyse_HM_obs(obs)
