import os, sys
import numpy as np
import pickle
import pandas as pd
from time import strftime
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.pyplot as plt


import helper


exp_id = helper.EXP_IDS[4]

wave_no = 0


def plot_results(timestamps, ax):
    for ts in timestamps:
        X = helper.get_flowrate_model(exp_id, ts)
        Y = np.array(range(helper.TOTAL_PEDS[exp_id]))
        ax.plot(X, Y, c='b')
    X, Y = helper.get_flowrate_data(exp_id)
    ax.plot(X, Y, c='r', linewidth=2)


def get_ens_var():
    ens_TS = helper.get_ensemble_timestamps(exp_id, wave_no)
    ens_outputs = [[helper.get_flowrate_coef(exp_id, ts) for ts in ens_group]
                   for ens_group in ens_TS]
    ens_var = 0
    for ens_group in ens_TS:
        ens_outputs = []
        for ts in ens_group:
            y = helper.get_flowrate_coef(exp_id, ts)
            if y != np.inf:
                ens_outputs.append(y)
        ens_var += np.var(ens_outputs)
    ens_var /= 2
    return ens_var


def get_coef_plaus_TS_indexes():
    TS = helper.get_tested_timestamps(exp_id, wave_no)
    obs = helper.get_flowrate_coef(exp_id, 'data')
    errors = [abs(obs - helper.get_flowrate_coef(exp_id, ts)) for ts in TS]
    ens_var = get_ens_var()

    scalar = 1
    plaus_TS_idxs = []
    while len(plaus_TS_idxs) < 3:
        implaus_scores = [e / (np.sqrt(ens_var)*scalar) for e in errors]
        plaus_TS_idxs = [i for i in range(len(TS)) if implaus_scores[i] < 3]
        scalar += 1
    #print(scalar)
    return plaus_TS_idxs


def get_exit_time_plaus_TS_indexes():
    ens_var = helper.load_results(exp_id)[0]['uncert']
    scalar = 1
    plaus_TS_idxs = []
    TS = helper.get_tested_timestamps(exp_id, wave_no)
    outputs = [helper.get_exit_time(exp_id, ts) for ts in TS]
    while len(plaus_TS_idxs) < 3:
        implaus_scores = [abs(y - helper.OBS[exp_id]) / (np.sqrt(ens_var)*scalar) for y in outputs]
        plaus_TS_idxs = [i for i in range(200) if implaus_scores[i] < 3]
        scalar += 1
    return plaus_TS_idxs


def plot_exit_vs_linear():
    fig, axs = plt.subplots(1, 2)

    TS = helper.get_tested_timestamps(exp_id, wave_no)
    plaus_TS_idxs = get_coef_plaus_TS_indexes()
    plaus_TS = [TS[i] for i in plaus_TS_idxs]
    plot_results(plaus_TS, axs[0])

    plaus_TS_idxs = get_exit_time_plaus_TS_indexes()
    plaus_TS = [TS[i] for i in plaus_TS_idxs]
    plot_results(plaus_TS, axs[1])

    axs[0].set_xlabel('t (s)')
    axs[1].set_xlabel('t (s)')
    axs[0].set_ylabel('cum. peds')
    plt.show()



if __name__ == '__main__':
    plot_exit_vs_linear()
