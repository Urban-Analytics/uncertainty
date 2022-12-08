import os
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
import helper


N = 4
FPS = 8
BOUNDS = {'force_ped_a': [0, 10],
          'force_ped_D': [0, 0.4],
          'v0_mu': [0.5, 1.9],
          'force_wall_a': [0, 10],
          'force_wall_D': [0, 0.08],
          #'T': [0, 2]
          }
FIG_LABELS = {'force_ped_a': r'$p_a$',
              'force_ped_D': r'$p_D$',
              'v0_mu': r'$v_\mu$',
              'force_wall_a': r'$w_a$',
              'force_wall_D': r'$w_D$',
              #'T': r'$T$'
              }

exp_id = 'runs_110_120'
obs = helper.OBS[exp_id]

# Choose the var that you're currently investigating.
#vars = ('force_ped_a', 'force_ped_D')
#results_subdir = 'runs_110_120_lowpeda/force_ped_aD'
vars = ('v0_mu',)
results_subdir = 'v0_mu_exit3'




inputs = {'force_ped_a': 1,
          'force_ped_D': 0.2,
          'v0_mu': 1.34,
          'force_wall_a': 1,
          'force_wall_D': 0.02}

# inputs = {'force_ped_a': 1.111275559073164,
#           'force_ped_D': 0.3740653300417453,
#           'v0_mu': 1.210018312075327,
#           'force_wall_a': 3.988670194816054,
#           'force_wall_D': 0.05983896316449987,
#           'T': 1
#           }


# Automatically generate the problem and choose the correct results directory.
# NOTE: run_model() doesn't update the chosen var automatically.
problem = {'num_vars': len(vars),
           'names': vars,
           'bounds': [BOUNDS[var] for var in vars]
          }


Y = []


def run_model():
    """ Run the model with the set of parameters X."""
    exit_time = run.run_sim_and_get_time((inputs['force_ped_a'],
                                          inputs['force_ped_D'],
                                          inputs['v0_mu'],
                                          inputs['force_wall_a'],
                                          inputs['force_wall_D']),
                                          ini_filename = '%s_ini.xml' % exp_id,
                                          results_subdir = 'sa/%s' % results_subdir)
    return exit_time


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
        # Update inputs
        for var_i in range(len(vars)):
            inputs[vars[var_i]] = X[var_i]
        y = run_model()
        Y.append(y)
    with open('results/sa/%s/exit_times.pkl' % results_subdir, 'wb') as pfile:
        pickle.dump(Y, pfile)


def get_sim_results():
    """ Fetch the population density results within the given zone. """
    try:
        with open('results/sa/%s/exit_times.pkl' % results_subdir, 'rb') as pfile:
            Y = pickle.load(pfile)
        return np.array(Y)
    except FileNotFoundError:
        with open('results/sa/%s/sa_timestamps.pkl' % results_subdir, 'rb') as pfile:
            TS = pickle.load(pfile)
        for timestamp in TS:
            fp = 'results/sa/%s/%s/%s_traj.txt' % (results_subdir, timestamp, exp_id)
            try:
                traj = pd.read_csv(fp, sep='\t', skiprows=12)
                frame_no = max(traj['FR'])  # get max frame number
                exit_times.append(frame_no / FPS)
            except pd.errors.EmptyDataError:
                exit_times.append(120)
        return exit_times


def run_sa_analysis():
    """ Calculate the sensitivity of each parameter for the given zone. """
    M = get_sim_results()
    print(sobol.analyze(problem, M)['S1'])
    # print(sobol.analyze(problem, M)['S2'])
    # print(sobol.analyze(problem, M)['ST'])


def plot_sim_results():
    param_values = get_param_values()
    Y = get_sim_results()
    print(len(param_values), len(Y))
    #Y = [abs(y - obs) for y in Y]
    plt.scatter(param_values, Y)
    plt.xlabel(FIG_LABELS[problem['names'][0]], fontsize=25)
    #plt.ylabel('error', fontsize=25)
    plt.ylabel(r'$f(x)$', fontsize=25)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    plt.show()


def plot_sim_results_two_var():
    def normalise(x, range1, range2):
        """ Rescale x from range1 to range2."""
        delta1 = range1[1] - range1[0]
        delta2 = range2[1] - range2[0]
        return (delta2 * (x - range1[0]) / delta1) + range2[0]

    def get_colours(output):
        """ Get colours for heatmap"""
        # normalise results to colour map (0, 255)
        # must make output an int for the colourmap to work correctly
        output = [int(normalise(x, (0, 120), (0, 255))) for x in output]
        return [cm.jet(d) for d in output]
    """ Plot the simulation output, given the both model parameters for each zone."""
    param_values = get_param_values()
    Y = get_sim_results()
    Y = [abs(y - obs) for y in Y]
    cax = plt.scatter(param_values[:,0],
                      param_values[:,1],
                      c=get_colours(Y))
    cbar = plt.colorbar(cax, ticks=(0, 1))
    plt.xlabel(vars[0].replace('_', ' '))
    plt.ylabel(vars[1].replace('_', ' '))
    #cbar.ax.get_yaxis().labelpad = 15
    cbar.ax.set_ylabel('error', rotation=270)
    cbar.ax.set_yticklabels(['0', str(max(Y))])
    plt.show()


if __name__ == '__main__':
    run_sa_problem()
    run_sa_analysis()
    plot_sim_results()
    #plot_sim_results_two_var()
