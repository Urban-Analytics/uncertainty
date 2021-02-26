import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.ticker import FixedLocator

import helper


# set manually
k = 100  # number of runs in ensembles
obs_unc = 0  # observation uncertainty
sigma = 3  # history matching threshold (commonly chosen as 3)

# set automatically
v_ens = 0  # ensemble variance
m_disc = 0  # model discrepancy


def v_ens_X(driver_indexes):
    """ Calculate the average variance over all plausible drivers."""
    results = dict((c, 0) for c in helper.OUTPUTS)
    for di in driver_indexes:
        results_x = v_ens_x(helper.drivers[di])
        for output in helper.OUTPUTS:
            results[output] += results_x[output]
    return dict((c, round(results[c]/len(driver_indexes), 3))
                for c in helper.OUTPUTS)


def v_ens_x(driver):
    """ Calculate the variance of a single plausible driver."""
    results = dict((c, []) for c in helper.OUTPUTS)
    for output in helper.OUTPUTS:
        r = []
        for i in range(k):
            df = pd.read_csv(helper.get_fp(driver, i+1))
            r.append(df[output].tolist())
        for a in range(k-1):
            for b in range(a+1, k):
                results[output].append(max(helper.error_func(r[a], r[b]),
                                        helper.error_func(r[b], r[a])))
    return dict((c, np.var(results[c], ddof=1)) for c in helper.OUTPUTS)


def m_disc_X(plaus_space):
    """ Calculate the average model discrepancy over all plausible drivers."""
    results = dict((output, 0) for output in helper.OUTPUTS)
    for di in plaus_space:
        driver_results = m_disc_x(helper.drivers[di])
        for output in helper.OUTPUTS:
            results[output] += driver_results[output]
    return dict((c, round(results[c]/len(plaus_space), 3))
                for c in helper.OUTPUTS)


def m_disc_x(driver):
    """ Calculate the model discrepancy of a single plausible driver."""
    results = {}
    df = pd.read_csv(helper.get_fp(driver))
    for output in helper.OUTPUTS:
        est = df[output].tolist()
        obs = helper.observations[output].tolist()
        e = helper.error_func(obs, est)
        results[output] = round(e, 3)
    return results


def implaus(driver):
    """ Calculate the implausibility of a set of parameters (drivers)."""
    estimates = pd.read_csv(helper.get_fp(driver))
    implaus = 0
    for output in helper.OUTPUTS:
        est = estimates[output].tolist()
        obs = helper.observations[output].tolist()
        diff = helper.error_func(obs, est)
        # Take the maximum implausiblity.
        # If the model is implausible for one output
        # then we're not interested in it.
        implaus = max(implaus,
                     diff / np.sqrt(v_ens[output] + m_disc[output] + obs_unc))
    return round(implaus, 4)


def wave(plaus_space):
    """ Run a wave of history matching.

        plaus_space: index of plausible helper.drivers to test.
        Returns: final plausible space, implausibility scores"""
    globals()['v_ens'] = v_ens_X(plaus_space)
    globals()['m_disc'] = m_disc_X(plaus_space)
    new_plaus_space = []
    implaus_scores = []
    for i in plaus_space:
        score = implaus(helper.drivers[i])
        implaus_scores.append(score)
        if score < sigma:
            new_plaus_space.append(i)
    return new_plaus_space, implaus_scores


def plot_implaus(plaus_space, implaus_scores):
    """ Plot the implausibility scores of the plaus_space."""
    fig, ax = plt.subplots()
    height = int(8)
    Z = np.empty((height, 2))
    for driver_i in range(16):
        x = int(driver_i / 2)
        y = driver_i % 2
        if driver_i in plaus_space:
            Z[x][y] = min(sigma, implaus_scores[plaus_space.index(driver_i)])
        else:
            Z[x][y] = 3
    im = plt.imshow(Z, cmap='pink_r', norm=Normalize(0, sigma))
    plt.colorbar(im)
    ax.xaxis.set_minor_locator(FixedLocator([-0.5, 0.5, 1.5]))
    ax.yaxis.set_minor_locator(FixedLocator(np.arange(-0.5, height)))
    ax.set_xticks((0, 1))
    ax.set_yticks(range(height))
    plt.grid(which='minor')
    #plt.savefig(strftime('hm_%Y%m%d_%H%M%S.pdf'))
    plt.show()


def history_matching():
    """ Run waves of history matching until the new plausible space
        is either empty (the whole space is implausible)
        or is unchanged from the previous wave.

        Returns: plausible space, uncertainty of each output
    """
    plaus_space = []
    new_plaus_space = range(len(helper.drivers))
    while len(new_plaus_space) > 0 and len(plaus_space) != len(new_plaus_space):
        plaus_space = new_plaus_space
        new_plaus_space, implaus_scores = wave(plaus_space)
        print('implausiblity scores: ', implaus_scores)
        print('new plausible space:', new_plaus_space)
        print('Ensemble variance:', v_ens)
        print('Model discrepancy:', m_disc)
        print('')
    uncert = dict((output, v_ens[output] +
                           m_disc[output] +
                           obs_unc)
                  for output in helper.OUTPUTS)
    return new_plaus_space, uncert


if __name__ == '__main__':
    plaus_space, uncert = history_matching()
    print('Final plausible space:', plaus_space)
    print('Uncertainties:', uncert)
