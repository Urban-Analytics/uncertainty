import os, sys
import numpy as np
import pickle
import pandas as pd
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.pyplot as plt
from sklearn import linear_model


samples  = 200

MODEL_FPS = 8
DIMENSIONS = 5
PARAMETERS = ('force_ped_a', 'force_ped_D', 'v_mu', 'force_wall_a', 'force_wall_D')


EXP_IDS = ('runs_110_120',
           'runs_230_240',
           'runs_270_280',
           'runs_050_060',
           'runs_030_040')


OBS = {'runs_110_120': 64.84,
       'runs_230_240': 38.24,
       'runs_270_280': 67.4,
       'runs_050_060': 40.52,
       'runs_030_040': 66.24}


DATA_FILENAMES = {'runs_110_120': 'data/Flow_NT_120_c_12_h-.txt_id_1.dat',
                  'runs_230_240': 'data/Flow_NT_240_q_23_h-.txt_id_1.dat',
                  'runs_270_280': 'data/Flow_NT_280_c_34_h-.txt_id_1.dat',
                  'runs_050_060': 'data/Flow_NT_060_c_45_h-.txt_id_1.dat',
                  'runs_030_040': 'data/Flow_NT_040_c_56_h-.txt_id_1.dat'}


TOTAL_PEDS = {'runs_110_120': 63,
              'runs_230_240': 42,
              'runs_270_280': 67,
              'runs_050_060': 42,
              'runs_030_040': 75}


def load_results(exp_id):
    """ Save results of all waves from pickle file. """
    filepath = 'results/%s_hm.pkl' % exp_id
    with open(filepath, 'rb') as pfile:
        return pickle.load(pfile)


def get_tested_timestamps(exp_id, wave_no):
    # last 40 are used to get ensemble variance
    start = wave_no * 240
    timestamps = sorted([f for f in os.listdir('results/%s/' % exp_id)])[start:start+samples]
    return timestamps


def get_ensemble_timestamps(exp_id, wave_no):
    start = 200 + (wave_no * 240)
    timestamps = sorted([f for f in os.listdir('results/%s/' % exp_id)])
    return (timestamps[start:start+20], timestamps[start+20:start+40])


def get_plaus_timestamps(exp_id, wave_no):
    results = load_results(exp_id)
    timestamps = get_tested_timestamps(exp_id, wave_no)
    plaus_indexes = [i for i in range(samples) if results[wave_no]['implaus_scores'][i] < 3]
    timestamps = [timestamps[i] for i in plaus_indexes]
    return timestamps


def get_exit_time(exp_id, timestamp):
    try:
        fp = 'results/%s/%s/%s_traj.txt' % (exp_id, timestamp, exp_id)
        traj = pd.read_csv(fp, sep='\t', skiprows=12)
        frame_no = max(traj['FR'])  # get max frame number
        return frame_no / MODEL_FPS
    except pd.errors.EmptyDataError:
        return 120


def get_flowrate_model(exp_id, timestamp):
    fp = 'results/%s/%s/%s_traj.txt' % (exp_id, timestamp, exp_id)
    traj = pd.read_csv(fp, sep='\t', skiprows=12)
    # get last frame each agent is in
    exit_times = np.empty(TOTAL_PEDS[exp_id])
    for agent_id in range(1, TOTAL_PEDS[exp_id]+1):
        exit_times[agent_id-1] = max(traj[traj['#ID'] == agent_id]['FR']) / MODEL_FPS
    exit_times.sort()
    return exit_times


def get_flowrate_data(exp_id):
    fp = 'results/reports/data/%s/Fundamental_Diagram/FlowVelocity/%s' % (exp_id[-3:], DATA_FILENAMES[exp_id])
    flow = pd.read_csv(fp, sep='\t', skiprows=2)
    X = flow['Time [s]']
    Y = flow['Cumulative pedestrians']
    return np.array(X), np.array(Y)


def get_flowrate_coef(exp_id, timestamp):
    model = linear_model.LinearRegression(fit_intercept=False)
    if timestamp == 'data':
        X, Y = get_flowrate_data(exp_id)
    else:
        X = get_flowrate_model(exp_id, timestamp)
        if X[-1] == 120:
            return np.inf
        Y = np.array(range(TOTAL_PEDS[exp_id]))
    X = X.reshape((-1, 1))
    model.fit(X,Y)
    return model.coef_[0]
