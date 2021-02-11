import math
import numpy as np
import random
import multiprocessing as mp
import os

# Required to set before running waves:
sim_func = None  # to run the simulation
error_func = None  # to calculate the error between simulation and observation
ensemble_func = None  # to run an ensemble of simulations
# to run the model with different parameters where each parameter is run once
variety_func = None

# Optional to set:
obs_var = 0  # the uncertainty in the observation (as variance)
k = 25  # total ensembles run for each input, change as desired
ensemble_samples = 4  # total samples used to average ensemble variance
# include model discrepancy when measuring uncertainty?
# sometimes it adds too much uncertainty resulting in all models accepted
include_model_disc = True

# Initially uknown and automatically calculated:
ens_var = 0  # ensemble variance
model_disc = 0  # model discrepancy
total_uncertainty = 0  # sum of all uncertainties


def variety_func(X):
    """ Run the model with a set of parameters X, each run once.

    This will need to be overridden if using a netlogo model. """
    pool = mp.Pool(mp.cpu_count())
    Y = pool.map(sim_func, X)
    pool.close()
    return Y


def run_k_times(x):
    """ Run the parameters x a total of k times. """
    return [sim_func(x) for _ in range(k)]


def ensemble_func(X, k):
    """ Run the model each parameter set in X a total of k times.

    This will need to be overridden if using a netlogo model. """
    pool = mp.Pool(mp.cpu_count())
    Y = pool.map_async(run_k_times, X).get()
    pool.close()
    return Y


def recalculate_uncertainties(X):
    """ Calculate the average uncertainties across inputs X.

    Each value x in X represents a different input parameter to test.
    Returns: (average ensemble variance across X,
              average model discrepancy across X)
    """
    vars = []
    discrepancies = []
    all_X_run_results = ensemble_func(X, k)
    for run_results in all_X_run_results:
        errors = [error_func(r) for r in run_results]
        vars.append(np.var(errors, ddof=1))
        discrepancies.append(np.mean(errors))
    globals()['ens_var'] = np.mean(vars)
    if include_model_disc:
        globals()['model_disc'] = np.mean(discrepancies)
    globals()['total_uncertainty'] = ens_var + obs_var + model_disc


def _implaus(y):
    """ Calculate the implausibility of the parameter x."""
    num = error_func(y)  # no emulator, only simulator
    denom = np.sqrt(total_uncertainty)  # only ensemble uncertainty
    return num / denom


def is_all_plausible(prev_plaus_space, new_plaus_space):
    """ Stopping criteria. Test if no new implausible space was found."""
    # If they're the same size, they must be the same
    return len(prev_plaus_space) == len(new_plaus_space)


def is_v_ens_x_small(new_plaus_space):
    """ Stopping criteria.
        Test if the variance of plausible space is less than model variance.
    """
    # add other uncertainties to the right side as they become included
    return np.var(new_plaus_space) < (total_uncertainty)


def wave(plaus_space):
    """ Run a wave of history matching.

    plaus_space is (for now) a list of discrete points.
    Returns the new plausible points found in plaus_space
    plus the implausibility scores.
    """
    # Get the new ensemble variance using a selection of three inputs from X,
    # where these inputs are evenly spread across the plausible space.
    # TODO: an optimised design, such as LHS, would be preferred.
    test_space = [plaus_space[i]
                 for i in range(0,
                                len(plaus_space),
                                math.ceil(len(plaus_space)/ensemble_samples))]
    recalculate_uncertainties(test_space)
    new_plaus_space = []
    Y = variety_func(plaus_space)
    implaus_scores = [_implaus(y) for y in Y]
    for i in range(len(plaus_space)):
        if implaus_scores[i] < 3:
            new_plaus_space.append(plaus_space[i])
    return total_uncertainty, new_plaus_space, implaus_scores
