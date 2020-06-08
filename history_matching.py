import math
import numpy as np
import random
import multiprocessing as mp


# set before running history matching waves
y = None  # observation
f = lambda x: None  # simulator


k = 25  # total ensembles run for each input (should be at least 25)
v_ens = 0  # ensemble variance; initially unknown; automatically calculated


def _v_ens_x(x):
    """ Calculate the ensemble variance for the input x. """
    return np.var([f(x) for _ in range(k)], ddof=1)


def v_ens_X(X):
    """ Calculate the average ensemble variance across inputs X.

    Each value x in X represents a different input parameter to test.
    Returns average of the variances for each x across k ensembles.
    """
    pool = mp.Pool(mp.cpu_count())
    vars_range = pool.map(_v_ens_x, X)
    pool.close()
    return np.mean(vars_range)


def _implaus(x):
    """ Calculate the implausibility of the parameter x."""
    num = abs(y - f(x))  # no emulator, only simulator
    denom = np.sqrt(v_ens)  # only ensemble uncertainty
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
    return np.var(new_plaus_space) < v_ens


def wave(plaus_space):
    """ Run a wave of history matching.

    plaus_space is (for now) a list of discrete points.
    Returns the new plausible points found in plaus_space
    plus the implausibility scores.
    """
    # Get the new ensemble variance using a selection of three inputs from X,
    # where these inputs are evenly spread across the plausible space.
    # In the future, an optimised design such as LHS, will be preferred.
    globals()['v_ens'] = v_ens_X([plaus_space[i]
                                     for i in range(0,
                                        len(plaus_space),
                                        math.ceil(len(plaus_space)/3))])
    new_plaus_space = []
    pool = mp.Pool(mp.cpu_count())
    implaus_scores = pool.map(_implaus, plaus_space)
    pool.close()
    for i in range(len(plaus_space)):
        if implaus_scores[i] < 3:
            new_plaus_space.append(plaus_space[i])
    return new_plaus_space, implaus_scores
