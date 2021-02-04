import math
import numpy as np
import random
import multiprocessing as mp
import os

# set before running history matching waves
sim_func = None  # to run the simulation
error_func = None  # to calculate error between simulation and observation
var_func = None  # to calculate the variance in an ensemble of simulations
obs_var = 0  # the uncertainty in the observation

include_model_disc = True
ensemble_samples = 4

k = 25  # total ensembles run for each input (should be at least 25)
ens_var = 0  # ensemble variance; initially unknown; automatically calculated
model_disc = 0
total_uncertainty = 0

def ensemble_func(x):
    """ Calculate the ensemble variance for the input x. """
    return [sim_func(x) for _ in range(k)]


def recalculate_uncertainties(X):
    """ Calculate the average ensemble variance across inputs X.

    Each value x in X represents a different input parameter to test.
    Returns average of the variances for each x across k ensembles.
    """
    pool = mp.Pool(mp.cpu_count())
    run_results = pool.map_async(ensemble_func, X).get()
    pool.close()
    vars = [np.var(r, ddof=1) for r in run_results]
    globals()['ens_var'] = np.mean(vars)
    errors = [np.mean([error_func(a) for a in r]) for r in run_results]
    if include_model_disc:
        globals()['model_disc'] = np.mean(errors)
    globals()['total_uncertainty'] = ens_var + obs_var + model_disc


def _implaus(x):
    """ Calculate the implausibility of the parameter x."""
    num = error_func(sim_func(x))  # no emulator, only simulator
    denom = np.sqrt(total_uncertainty)  # only ensemble uncertainty
    return num / denom


def is_all_plausible(prev_plaus_space, new_plaus_space):
    """ Stopping criteria. Test if no new implausible space was found."""
    # If they're the same size, they must be the same
    # NOTE: that this method will likely need to be updated if we change
    # the plausible space to not always be discrete and convex
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
    # In the future, an optimised design such as LHS, will be preferred.
    test_space = [plaus_space[i]
                 for i in range(0,
                                len(plaus_space),
                                math.ceil(len(plaus_space)/ensemble_samples))]
    recalculate_uncertainties(test_space)
    new_plaus_space = []
    pool = mp.Pool(mp.cpu_count())
    implaus_scores = pool.map(_implaus, plaus_space)
    pool.close()
    for i in range(len(plaus_space)):
        if implaus_scores[i] < 3:
            new_plaus_space.append(plaus_space[i])
    return total_uncertainty, new_plaus_space, implaus_scores
