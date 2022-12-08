from SALib.sample import saltelli, fast_sampler
from SALib.analyze import sobol
import numpy as np
import pickle
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd

import run


N = 20
REPORT_FP = '/Fundamental_Diagram/Classical_Voronoi/rho_v_Voronoi_Voronoi_traj.txt_id_'
BOUNDS = {'force_ped_a': [0, 10],
          'force_ped_D': [0, 1],
          'v0_mu': [0.5, 1.6],
          'force_wall_a': [0, 10],
          'force_wall_D': [0, 0.1]}
FIG_LABELS = {'force_ped_a': r'$p_a$',
              'force_ped_D': r'$p_D$',
              'v0_mu': r'$v_\mu$',
              'force_wall_a': r'$w_a$',
              'force_wall_D': r'$w_D$'}


# Choose the var that you're currently investigating.
var = 'force_wall_a'

# Automatically generate the problem and choose the correct results directory.
# NOTE: run_model() doesn't update the chosen var automatically.
problem = {'num_vars': 1,
           'names': [var],
           'bounds': [BOUNDS[var]]
          }
results_dir = 'results/SA/%s' % var


# Keep an ordered list of timestamps so that the model results
# can be loaded in the correct order (which is chronological, anyway).
# This enables you to organise which timetamps are associated with which tests.
timestamps = []


def run_model(X):
    """ Run the model with the set of parameters X."""
    timestamp = run.change_config_core(force_wall_D=X[0], results_dir=results_dir)
    run.run()
    return timestamp


def get_param_values():
    """ Generate parameters using the defined problem. """
    return saltelli.sample(problem, N)
    #return fast_sampler.sample(problem, N)


def run_sa_problem():
    """ Run the model using parameters generated for the defined problem.
    Note this doesn't generate the model report.
    """
    # Generate parameter values
    param_values = get_param_values()
    print(len(param_values))
    # Run the model
    # jupedsim runs multicore so no need to do any multiprocessing
    for X in param_values:
        timestamp = run_model(X)
        timestamps.append(timestamp)
    with open('%s/sa_timestamps.pkl' % results_dir, 'wb') as pfile:
        pickle.dump(timestamps, pfile)


def run_jupedsim_report():
    """ Calculate the population densities from the simulation runs. """
    with open('%s/sa_timestamps.pkl' % results_dir, 'rb') as pfile:
        timestamps = pickle.load(pfile)
    for t in timestamps:
        run.change_config_report(t, results_dir)
        run.report()


def get_report_results(zone_no=1):
    """ Fetch the population density results within the given zone. """
    with open('%s/sa_timestamps.pkl' % results_dir, 'rb') as pfile:
        timestamps = pickle.load(pfile)
    n = len(timestamps)
    M = np.zeros(n)
    for t in range(n):
        fp = '%s/report_results_%s%s%d.dat' % (results_dir, timestamps[t], REPORT_FP, zone_no)
        zone = pd.read_csv(fp, sep='\t', skiprows=2)
        # fix reading of columns
        zone.pop('Voronoi velocity(m/s)')
        zone.columns = ['frame', 'density', 'velocity']
        M[t] = np.mean(zone['density'])
    return M



def run_sa_analysis(zone_no=1):
    """ Calculate the sensitivity of each parameter for the given zone. """
    M = get_report_results(zone_no)
    print(sobol.analyze(problem, M)['S1'])
    # print(sobol.analyze(problem, M)['S2'])
    # print(sobol.analyze(problem, M)['ST'])


def plot_sim_results():
    param_values = get_param_values()
    M1 = get_report_results(zone_no=1)
    plt.scatter(param_values, M1, marker='+')
    M2 = get_report_results(zone_no=2)
    plt.scatter(param_values, M2, marker='o')
    plt.xlabel(FIG_LABELS[problem['names'][0]], fontsize=25)
    #plt.ylabel(r'$f_%d(x)$' % zone_no, fontsize=16)
    plt.ylabel(r'$f_i(x)$', fontsize=25)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    if var == 'v0_mu':
        plt.ylim(0, 0.16)
    else:
        plt.ylim(0, 0.07)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    # run_sa_problem()
    # run_jupedsim_report()
    #run_sa_analysis(1)
    plot_sim_results()
