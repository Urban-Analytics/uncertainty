import math
import matplotlib.pyplot as plt
import numpy as np
import random


# set before running history matching waves
y = None  # observation
f = lambda x: None  # simulator


k = 25  # total ensembles run for each input (should be at least 25)
v_ens = 0  # ensemble variance; initially unknown; automatically calculated


def _get_v_ens(X):
    """ Calculate ensemble variance for inputs X.

    Each value x in X represents a different input parameter to test.
    Returns average of the variances for each x across k ensembles.
    """
    vars_range = []
    for x in X:
        vars_range.append(np.var([f(x) for _ in range(k)], ddof=1))
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
    return prev_plaus_space.size == new_plaus_space.size


def is_var_small(new_plaus_space):
    """ Stopping criteria.
        Test if the variance of plausible space is less than model variance.
    """
    # add other uncertainties to the right side as they become included
    return np.var(new_plaus_space) < v_ens


def wave(plaus_space, plot=False):
    """ Run a wave of history matching.

    plaus_space is (for now) a list of discrete points in a convex space.
    Returns the new plausible points found in plaus_space.
    """
    # get new ensemble variance
    globals()['v_ens'] = _get_v_ens([plaus_space[i]
                                     for i in range(0,
                                        len(plaus_space),
                                        math.ceil(len(plaus_space)/3))])
    new_plaus_space = []
    plt.clf()
    for x in plaus_space:
        score = _implaus(x)
        if score < 3:
            plt.scatter(x, score, color=u'#1f77b4')
            new_plaus_space.append(x)
        else:
            plt.scatter(x, score, color=u'#ff7f0e')
    plt.axhline(y=3, xmin=0, xmax=1)
    plt.xlim(min(new_plaus_space), max(new_plaus_space))
    if plot:
        plt.xlim(min(plaus_space), max(plaus_space))
        plt.show()
    return np.array(new_plaus_space)
