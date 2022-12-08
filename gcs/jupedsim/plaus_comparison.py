""" Find the proportion of tests that were found to be plausible from
    history matching in a given zone (base) and were also found to be
    plausible in a different zone (comparison).
"""

import os, sys
import numpy as np
import pandas as pd
import pickle

import jupedsim_hm


REPORT_FP = '/Fundamental_Diagram/Classical_Voronoi/rho_v_Voronoi_Voronoi_traj.txt_id_'
dirs = {1:'results/211208_151221', 2:'results/220110_134905', 3:'results/220117_104155'}
plaus_zone = 3  #base
comparison_zone = 1

# Get observation for both zones
obs = None
with open('../data/average_density_zone%d.pkl' % comparison_zone, 'rb') as pfile:
    obs = pickle.load(pfile)

def simulation_density(timestamp):
    """ Get the population density for a given run report. """
    fp = '%s/report_results_%s%s%d.dat' % (dirs[plaus_zone], timestamp, REPORT_FP, comparison_zone)
    zone = pd.read_csv(fp, sep='\t', skiprows=2)
    # fix reading of columns
    zone.pop('Voronoi velocity(m/s)')
    zone.columns = ['frame', 'density', 'velocity']
    # temp code to get variance
    model_vars_sum = np.var(zone['density'], ddof=1)
    return np.mean(zone['density'])

def error(timestamp):
    return abs(simulation_density(timestamp) - obs)

def implaus(timestamp, uncert):
    """ Calculate the implausibility of the parameter x."""
    num = error(timestamp)  # no emulator, only simulator
    denom = np.sqrt(uncert)  # only ensemble uncertainty
    return num / denom


def variance(stamps1, stamps2):
    v = 0
    for stamps in (stamps1, stamps2):
        errors = [error(ts) for ts in stamps]
        v += np.var(errors, ddof=1)
    return v / 2


def plaus_timestamps(results_dir):
    """ Get the timestamps that produced plausible results in the final wave of history matching."""
    # Get the HM results
    with open('%s_hm.pkl' % results_dir, 'rb') as pfile:
        hm_results = pickle.load(pfile)
    # Find out how many samples were in the last wave
    total_samples = len(hm_results[-1]['plaus_space'])
    # Find out which samples were found to be plausible
    ps = []
    for i in range(total_samples):
        if hm_results[-1]['implaus_scores'][i] < 3:
            x = hm_results[-1]['plaus_space'][i]
            ps.append((round(x[0], 8), round(x[1], 8), round(x[2], 8)))
    # Runs are stored in alphabetical (numerical) order by timestamp.
    # Sort the timestamps and get the last (total_samples) to get the final wave.
    # The implaus scores are sorted in the same order so the plausible runs are easily obtained
    timestamps = sorted([f[15:] for f in os.listdir(results_dir) if f.startswith('report_results_')])[-total_samples:]
    return [timestamps[i] for i in range(total_samples) if hm_results[-1]['implaus_scores'][i] < 3]


timestamps = sorted([f[15:] for f in os.listdir(dirs[plaus_zone]) if f.startswith('report_results_')])
plaus_stamps = plaus_timestamps(dirs[plaus_zone])
print(len(plaus_stamps))
var_stamps1 = timestamps[-80:-50]
var_stamps2 = timestamps[-110:-80]
uncert = variance(var_stamps1, var_stamps2)
implaus_scores = [implaus(ts, uncert) for ts in plaus_stamps]
print(len([s for s in implaus_scores if s < 3]))
