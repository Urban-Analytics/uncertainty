import pickle
from typing import NamedTuple

import hoopoes_hm as hhm


DIMENSIONS = 2
PARAMETERS = ['scout_prob', 'survival_prob']


class params(NamedTuple):
    """ Parameters given to the Hoopoes model. """
    scout_prob: int
    survival_prob: int


class result(NamedTuple):
    """ The 'observation' that resulting from the Hoopoes model. """
    parameters: params
    obs: int
    results_dir: str


def split(params):
    """ Split params NamedTuple into regular tuple. """
    return [params.scout_prob, params.survival_prob]


def get_bounds(X):
    """ Get the smallest and largest value for each parameter."""
    bounds = {}
    for d in range(DIMENSIONS):
        lst = [x[d] for x in X]
        bounds[PARAMETERS[d]] = (min(lst), max(lst))
    return bounds


def in_bound(x, bound):
    """ Check if x is within the boundary. """
    return bound[0] <= x <= bound[1]


def bound_len(bound):
    """ Get the length of the boundary. """
    return bound[1] - bound[0]


def last_wave(results_dir):
    """ Get the plausible space of the final wave from HM. """
    with open(results_dir + '/hm.pkl', 'rb') as pfile:
        hm_results = pickle.load(pfile)
    end_wave = hm_results[-1]
    accepted_space = [end_wave['plaus_space'][i]
                      for i in range(len(end_wave['plaus_space']))
                      if end_wave['implaus_scores'][i] < 3]
    return accepted_space


def uncertainty(results_dir):
    """ Get the uncertainty measured in the final wave of HM. """
    with open(results_dir + '/hm.pkl', 'rb') as pfile:
        hm_results = pickle.load(pfile)
    return hm_results[-1]['uncert']


def hm_total_runs(observations):
    """ Calculate the total model runs used by HM. """
    totals = []
    for obs in observations:
        with open(obs.results_dir + '/hm.pkl', 'rb') as pfile:
            hm_results = pickle.load(pfile)
        total = (len(hm_results) * hhm.samples) + \
                (len(hm_results) * hhm.history_matching.k * hhm.history_matching.ensemble_samples)
        totals.append(total)
    return totals
