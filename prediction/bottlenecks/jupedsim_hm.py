import os, sys
import numpy as np
import pickle
import lhsmdu
import pandas as pd
from time import strftime
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.pyplot as plt
#import plotly.express as px
import plotly.graph_objects as go


import history_matching as hm
import run

exp_id = 'runs_050_060'
samples  = 200


FPS = 8
DIMENSIONS = 5
PARAMETERS = ('force_ped_a', 'force_ped_D', 'v_mu', 'force_wall_a', 'force_wall_D')
# Default bounds
BOUNDS = {'force_ped_a': (0, 6),
          'force_ped_D': (0, 1),
          'v_mu': (0.5, 1.6),
          'force_wall_a': (0, 8),
          'force_wall_D': (0, 0.1) }


results = []

OBS = {'runs_110_120': 64.84,
       'runs_230_240': 38.24,
       'runs_270_280': 67.4,
       'runs_050_060': 40.52,
       'runs_030_040': 66.24}

# OBS = {'runs_110_120': 61.875} # random model run



def run_sim_and_get_time(x):
    """ Run Jupedsim core. """
    timestamp = run.run(x, '%s_ini.xml' % exp_id)
    try:
        fp = 'results/%s/%s/%s_traj.txt' % (exp_id, timestamp, exp_id)
        traj = pd.read_csv(fp, sep='\t', skiprows=12)
        frame_no = max(traj['FR'])  # get max frame number
        return frame_no / FPS
    except pd.errors.EmptyDataError:
        return 120


# Overwrite the hm multiprocessing function (jupedsim already does multiprocessing)
def variety_func(X):
    """ Run the model with a set of parameters X, each run once. """
    return [run_sim_and_get_time(x) for x in X]


# Overwrite the hm multiprocessing function (jupedsim already does multiprocessing)
def ensemble_func(X, k):
    """ Run the model each parameter set in X a total of k times. """
    return [[run_sim_and_get_time(x) for _ in range(k)] for x in X]


def calculate_error(y):
    return abs(y - OBS[exp_id])


def init_sample():
    """ Use LHS design to create samples for the first wave. """
    def bind_list(X, param):
        """ Scale values in a list so the smallest and largest values
        are the same as the provided for the parameter."""
        return X * (BOUNDS[param][1] - BOUNDS[param][0]) + BOUNDS[param][0]
    lhsmdu.setRandomSeed(12)
    X = lhsmdu.sample(DIMENSIONS, samples)
    for i in range(DIMENSIONS):
        X[i] = bind_list(X[i], PARAMETERS[i])
    X = X.T
    X = X.tolist()
    return X


def resample(X):
    """ Resample X within the mean and 1.2*std of the plausible samples."""
    def bind_value(x, limits):
        """ Bring a single within the limits if it has fallen outside."""
        x = max(BOUNDS[limits][0], x)
        x = min(BOUNDS[limits][1], x)
        return x
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


def save_results():
    """ Save results of all waves using pickle. """
    # overwrites save of the previous wave
    filepath = 'results/%s_hm.pkl' % exp_id
    with open(filepath, 'wb') as pfile:
        pickle.dump(results, pfile)


def load_results():
    """ Save results of all waves from pickle file. """
    filepath = 'results/%s_hm.pkl' % exp_id
    with open(filepath, 'rb') as pfile:
        return pickle.load(pfile)


def plaus_space_decreased(plaus_space, new_plaus_space):
    if len(plaus_space) == 0:
        return True  # to initiate first wave
    for d in range(DIMENSIONS):
        old = [x[d] for x in plaus_space]
        new = [x[d] for x in new_plaus_space]
        if min(old) < min(new) or max(old) > max(new):
            return True
    return False


def plot(waves, exclude_implaus=True, show=True, filename='hm_results'):
    samples = len(waves[0]['plaus_space'])  # in case different to default
    # Rename zone 3 to zone 0
    df = pd.DataFrame(np.concatenate([wave['plaus_space'] for wave in waves]),
                      columns=(PARAMETERS))
    df['implaus_scores'] = np.concatenate([wave['implaus_scores'] for wave in waves])

    # remove implausible results
    if exclude_implaus:
        df = df[df.implaus_scores < 3]
        df["implaus_scores"] = 0
    else:
        df["implaus_scores"] = np.where(df["implaus_scores"] < 3, 0, 1)

    # df['outputs'] = np.concatenate([wave['outputs'] for wave in waves])
    # df = df[df.outputs < 120]

    dimensions = [dict(range = (BOUNDS[PARAMETERS[i]][0], BOUNDS[PARAMETERS[i]][1]),
                       label = PARAMETERS[i].replace('_', ' '),
                       values = df[PARAMETERS[i]])
                  for i in range(DIMENSIONS)]

    if not exclude_implaus:
        dimensions.append(dict(range = (0, 1),
                                  label = 'Implausible?',
                                  tickvals = (0, 1),
                                  values = df['implaus_scores']))

    fig = go.Figure(data=
        go.Parcoords(
            line = dict(color = df['implaus_scores'],
                      colorscale = [[0, '#4682B4'], [1,'#FF8C00']]),
            dimensions = dimensions
                )
            )
    fig.layout = {'font_size':22, 'title':exp_id}
    D = fig.to_dict()["data"][0]["dimensions"]
    R = [np.linspace(BOUNDS[PARAMETERS[i]][0], BOUNDS[PARAMETERS[i]][1], 5)
         for i in range(DIMENSIONS)]
    if not exclude_implaus:
        R.append((0, 1))
    fig.update_traces(
        dimensions=[
            {**D[i], **{"tickvals": R[i]}}
            for i in range(len(D))
        ]
    )
    if show:
        fig.show()
    else:
        fig.write_image('results/%s.pdf' % filename)


def run_waves(waves=None):
    # initialise HM
    hm.sim_func = run_sim_and_get_time
    hm.error_func = calculate_error
    # overwrite the hm multiprocessing functions (jupedsim already does multiprocessing)
    hm.variety_func = variety_func
    hm.ensemble_func = ensemble_func
    # create results folder
    global results
    if waves == None:
        # initialise first wave
        wave_no = 1
        new_plaus_space = init_sample()
        plaus_space = []
    else:
        results = waves
        wave_no = waves[-1]['wave_no'] + 1
        plaus_space = waves[-1]['plaus_space']
        new_plaus_space = [waves[-1]['plaus_space'][i] for i in range(samples)
                           if waves[-1]['implaus_scores'][i] < 3]
    # Stop if the plausible space has not narrowed any smaller,
    # or if only one or no samples are plausible,
    # or until 5 waves have occured (I'm not waiting forever).
    while (wave_no <= 1 and len(new_plaus_space) > 1
                 and plaus_space_decreased(plaus_space, new_plaus_space)):
        plaus_space = new_plaus_space
        if wave_no > 1:
            # Explore around the plausible space found,
            # rather than retesting the same samples as the previous wave
            plaus_space = resample(plaus_space)
        uncert, new_plaus_space, implaus_scores, outputs = hm.wave(plaus_space)
        results.append({'wave_no': wave_no,
                        'uncert': uncert,
                        'plaus_space': plaus_space,
                        'implaus_scores': implaus_scores,
                        'outputs': outputs})
        print(results[-1])
        wave_no += 1
        print(len(new_plaus_space))
        #plot_wave(results[-1])
        # save results at each iteration so they can be examined during runtime
        save_results()


def foo():
    import math
    hm.sim_func = run_sim_and_get_time
    hm.error_func = calculate_error
    hm.variety_func = variety_func
    hm.ensemble_func = ensemble_func
    global results
    results = load_results()
    Y = results[-1]['outputs']
    hm.total_uncertainty = 1.468628826530612
    results[-1]['uncert'] = hm.total_uncertainty
    implaus_scores = [hm._implaus(y) for y in Y]
    results[-1]['implaus_scores'] = implaus_scores
    save_results()


if __name__ == '__main__':
    run_waves()
    #run_waves(load_results())
    #results = load_results()
    wave_no = -1
    #r = [results[wave_no]['outputs'][i] for i in range(samples) if results[wave_no]['implaus_scores'][i] < 3]
    #print(r)
    # #print(results)
    # #print(results[1]['wave_no'])
    plot((results[wave_no],), exclude_implaus=True)
    #print(results[-1]['uncert'])
    # m = np.mean(r)
    # std = np.std(r)
    # lower = m - (3 * (std))
    # upper = m + (3 * (std))
    # r = [y for y in r if lower <= y < 120]
    # n, b, p = plt.hist(r, alpha=0.5)
    #
    # plt.vlines(x=OBS[exp_id], ymin=0, ymax=max(n))
    # plt.show()
    #foo()
