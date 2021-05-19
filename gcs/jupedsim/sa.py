from SALib.sample import saltelli
from SALib.analyze import sobol
from SALib.test_functions import Ishigami
import numpy as np
import multiprocessing as mp
import pickle
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd

import run

N = 50
report_fp = '/Fundamental_Diagram/Classical_Voronoi/rho_v_Voronoi_Voronoi_traj.txt_id_'

problem = {'num_vars': 2,
           'names': ['force_ped', 'force_wall'],
           'bounds': [[1, 10], [1, 10]]
          }

# Keep an ordered list of timestamps so that the model results
# can be loaded in the correct order.
timestamps = []


def run_model(X):
    timestamp = run.run_with_change({'a':str(X[0]), 'D':'0.2'},
                                   {'a':str(X[1]), 'D':'0.02'})
    return timestamp


def get_param_values():
    return saltelli.sample(problem, N)

def run_sa_problem():
    # Generate parameter values
    param_values = get_param_values()
    print(len(param_values))
    # Run the model
    # jupedsim runs multicore so no need to do any multiprocessing
    for X in param_values:
        timestamp = run_model(X)
        timestamps.append(timestamp)
    with open('results/sa_timestamps.pkl', 'wb') as pfile:
        pickle.dump(timestamps, pfile)


def run_jupedsim_report():
    with open('results/sa_timestamps.pkl', 'rb') as pfile:
        timestamps = pickle.load(pfile)
    for t in timestamps:
        print(t)
        run.change_config_report(t)
        run.report()


def get_report_results(zone_no=1):
    M = np.zeros(300)  # work out, don't hard code the 300
    SIGMA = np.zeros(300)
    with open('results/sa_timestamps.pkl', 'rb') as pfile:
        timestamps = pickle.load(pfile)
    for t in range(300):
        fp = 'results/report_results_%s%s%d.dat' % (timestamps[t], report_fp, zone_no)
        zone = pd.read_csv(fp, sep='\t', skiprows=2)
        # fix reading of columns
        zone.pop('Voronoi velocity(m/s)')
        zone.columns = ['frame', 'density', 'velocity']
        M[t] = np.mean(zone['density'])
        SIGMA[t] = np.var(zone['density'], ddof=1)
    return M, SIGMA



def run_sa_analysis(zone_no=2):
    M, SIGMA = get_report_results(zone_no)
    Si = sobol.analyze(problem, M)['S1']
    print(Si)
    Si = sobol.analyze(problem, SIGMA)['S1']
    print(Si)



def plot_sim_results(zone_no):
    def normalise(n, range1, range2):
        """ To normalise results within heatmap colour range."""
        delta1 = range1[1] - range1[0]
        delta2 = range2[1] - range2[0]
        return (delta2 * (n - range1[0]) / delta1) + range2[0]
    def get_colours(output):
        # normalise results to colour map (0, 255)
        min_d = min(output)
        max_d = max(output)
        # must make density an int for the colourmap to work correctly
        output = [int(normalise(d, (min_d, max_d), (0, 255))) for d in output]
        return [cm.jet(d) for d in output]

    fig, ax = plt.subplots(3, 2)
    M, SIGMA = get_report_results(zone_no)
    param_values = get_param_values()
    ax[0][0].scatter(param_values[:,0], M)
    ax[1][0].scatter(param_values[:,1], M)
    ax[0][1].scatter(param_values[:,0], SIGMA)
    ax[1][1].scatter(param_values[:,1], SIGMA)
    ax[2][0].scatter(param_values[:,0], param_values[:,1], c=get_colours(M))
    ax[2][1].scatter(param_values[:,0], param_values[:,1], c=get_colours(SIGMA))
    plt.show()


if __name__ == '__main__':
    #run_sa_analysis(1)
    plot_sim_results(1)
