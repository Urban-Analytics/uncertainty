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


# import history_matching from parent directory
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)
import history_matching as hm

import run


zone_no = 2  # The current zone analysed. Change as desired.
samples  = 50

# filepath of report results
REPORT_FP = '/Fundamental_Diagram/Classical_Voronoi/rho_v_Voronoi_Voronoi_traj.txt_id_'

DIMENSIONS = 3
PARAMETERS = ('force_ped_a', 'force_ped_D', 'v_mu')
# Default bounds
BOUNDS = {'force_ped_a': (0, 6),
          'force_ped_D': (0, 1),
          'v_mu': (0.5, 1.6) }

# zone 1 output
# BOUNDS = {'force_ped_a': (0.801685, 5.389310),
#           'force_ped_D': (0.088666, 0.985913),
#           'v_mu': (0.891905, 1.120964)}

# zone 2 output
# BOUNDS = {'force_ped_a': (0.000000, 6.000000),
#           'force_ped_D': (0.481304, 1.000000),
#           'v_mu': (0.558162, 0.800518)}

results = []
results_dir = ''

#Get observation for the zones from the data
obs = {}
for i in (1, 2, 3, 4, 5, 6, 7):
    with open('../data/average_density_zone%d.pkl' % i, 'rb') as pfile:
        obs[i] = pickle.load(pfile)[1]


# Get observations from a 'true' model run
# import analyse_density_model
# obs = dict((zn, analyse_density_model.get_zone('results/true/report_results_true%s%d.dat' % (REPORT_FP, zn)))
#             for zn in range(1, 4))


def simulation_density(timestamp):
    """ Get the population density for a given run report. """
    fp = '%s/report_results_%s%s%d.dat' % (results_dir, timestamp, REPORT_FP, zone_no)
    zone = pd.read_csv(fp, sep='\t', skiprows=2)
    # fix reading of columns
    zone.pop('Voronoi velocity(m/s)')
    zone.columns = ['frame', 'density', 'velocity']
    # temp code to get variance
    model_vars_sum = np.var(zone['density'], ddof=1)
    return np.mean(zone['density'])


def run_sim_and_get_density(x):
    """ Run Jupedsim core and report. """
    timestamp = run.run_with_change(x, results_dir)
    run.change_config_report(timestamp, results_dir)
    run.report()
    return simulation_density(timestamp)


# Overwrite the hm multiprocessing function (jupedsim already does multiprocessing)
def variety_func(X):
    """ Run the model with a set of parameters X, each run once. """
    return [run_sim_and_get_density(x) for x in X]


# Overwrite the hm multiprocessing function (jupedsim already does multiprocessing)
def ensemble_func(X, k):
    """ Run the model each parameter set in X a total of k times. """
    return [[run_sim_and_get_density(x) for _ in range(k)] for x in X]


def calculate_error(density):
    return abs(density - obs[zone_no])



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


def plot_sampled_values():
    X = np.array(init_sample())
    X0 = X[:,0]
    X1 = X[:,1]
    X2 = X[:,2]
    dimensions = list([
        dict(range = (0, max(X0)),
            label = PARAMETERS[0].replace('_', ' '), values = X0),
        dict(range = (0, max(X1)),
            label = PARAMETERS[1].replace('_', ' '), values = X1),
        dict(range = (0.5, max(X2)),
            label = PARAMETERS[2].replace('_', ' '), values = X2),
            ])
    fig = go.Figure(data=
        go.Parcoords(
            dimensions = dimensions
                )
        )
    fig.show()



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


def save_results(timestamp):
    """ Save results of all waves using pickle. """
    # overwrites save of the previous wave
    filepath = 'results/%s_hm.pkl' % timestamp
    with open(filepath, 'wb') as pfile:
        pickle.dump(results, pfile)


def load_results(timestamp):
    """ Save results of all waves from pickle file. """
    filepath = 'results/%s_hm.pkl' % timestamp
    with open(filepath, 'rb') as pfile:
        return pickle.load(pfile)


def plot_zones_parallel(waves, exclude_implaus=True, show=True, filename='hm_results'):
    samples = len(waves[0]['plaus_space'])  # in case different to default
    # Rename zone 3 to zone 0
    for wave in waves:
        if wave['zone_no'] == 3:
            wave['zone_no'] = 0
    df = pd.DataFrame(np.concatenate([wave['plaus_space'] for wave in waves]),
                      columns=(PARAMETERS))
    df['implaus_scores'] = np.concatenate([wave['implaus_scores'] for wave in waves])
    df['zone'] = np.concatenate([[wave['zone_no'] for _ in range(samples)]
                                 for wave in waves])
    # remove implausible results
    if exclude_implaus:
        df = df[df.implaus_scores < 3]
    else:
        df["implaus_scores"] = np.where(df["implaus_scores"] < 3, 0, 1)
        #df.loc[df['implaus_scores'] < 3] = 0
        #df.loc[df['implaus_scores'] >= 3] = 1
        #pass
    # make column labels looks nicer
    #fig_labels = dict((c, c.replace('_', ' ')) for c in df.columns)
    #fig_labels = (r'$f_a$', r'$f_D$', r'$v_\mu$', 'implaus scores', 'zone')  # latex tables come out poor quality
    #df.columns = fig_labels
    #fig = px.parallel_coordinates(df, color='zone')
    dimensions = [dict(range = (BOUNDS[PARAMETERS[i]][0], BOUNDS[PARAMETERS[i]][1]),
                       label = PARAMETERS[i].replace('_', ' '),
                       values = df[PARAMETERS[i]])
                  for i in range(DIMENSIONS)]

    if not exclude_implaus:
        dimensions.append(dict(range = (0, 1),
                                  label = 'Implausible?',
                                  tickvals = (0, 1),
                                  values = df['implaus_scores']))

    dimensions.append(dict(range = (0, max(df.zone)),
                      tickvals = list(range(0, max(df.zone)+1)),
                      label = 'zone',
                      values = df['zone']))

    fig = go.Figure(data=
        go.Parcoords(
            line = dict(color = df['zone'],
                      colorscale = [[0, '#ee0000'],[0.5, '#ec7600'],[1,'#55007f']]),
            dimensions = dimensions
                )
            )
    fig.layout = {'font_size':22}
    D = fig.to_dict()["data"][0]["dimensions"]
    R = [np.linspace(BOUNDS[PARAMETERS[i]][0], BOUNDS[PARAMETERS[i]][1], 5)
         for i in range(DIMENSIONS)]
    if not exclude_implaus:
        R.append((0, 1))
    R.append((0, 1, 2))
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


def plot(waves, show=True, highlightzone=-1):
    def convert(old_value, new_bounds, old_bounds):
        old_min, old_max = old_bounds
        new_min, new_max = new_bounds
        old_range = (old_max - old_min)
        new_range = (new_max - new_min)
        return (((old_value - old_min) * new_range) / old_range) + new_min

    FIG_LABELS = (r'$p_a$', r'$p_D$', r'$v_\mu$', r'$i$')
    samples = len(waves[0]['plaus_space'])  # in case different to default
    # Rename zone 3 to zone 0
    for wave in waves:
        if wave['zone_no'] == 3:
            wave['zone_no'] = 0
    df = pd.DataFrame(np.concatenate([wave['plaus_space'] for wave in waves]),
                      columns=(PARAMETERS))
    df['implaus_scores'] = np.concatenate([wave['implaus_scores'] for wave in waves])
    df['zone'] = np.concatenate([[wave['zone_no'] for _ in range(samples)]
                                 for wave in waves])
    # remove implausible results
    df = df[df.implaus_scores < 3]
    IDX, FORCEA, FORCED, VMU, IMPLAUS, ZONE = range(6)
    C = ('seagreen', 'darkorange', 'purple')
    x = range(4)
    fig, ax = plt.subplots(1, 4, sharey=False)
    for i in range(3):
        for row in df.itertuples():
            if highlightzone == -1:
                alpha = 0.7
            else:
                if row[ZONE] == highlightzone:
                    alpha = 0.8
                else:
                    alpha = 0.2
            # Each y-axis has different limits so you need to convert each plot line
            # to be compatible with each y-axis
            row_forcea = convert(row[FORCEA], BOUNDS[PARAMETERS[i]], BOUNDS[PARAMETERS[0]])
            row_forceD = convert(row[FORCED], BOUNDS[PARAMETERS[i]], BOUNDS[PARAMETERS[1]])
            row_vmu = convert(row[VMU], BOUNDS[PARAMETERS[i]], BOUNDS[PARAMETERS[2]])
            row_zone = convert(row[ZONE], BOUNDS[PARAMETERS[i]], (0, 2))
            ax[i].plot(x, (row_forcea, row_forceD, row_vmu, row_zone), c=C[row[ZONE]], linewidth=1, alpha=alpha)
        ax[i].set_xlim([x[i],x[i]+1])
        ax[i].set_xticks((x[i],))
        ax[i].set_xticklabels((FIG_LABELS[i],), fontsize=16)
        ax[i].spines['bottom'].set_color('white')
        ax[i].set_ylim(BOUNDS[PARAMETERS[i]])
    ax[3].set_ylim((0, 2))
    ax[3].set_yticks((0, 1, 2))
    ax[3].set_xticks((0,))
    ax[3].set_xticklabels((FIG_LABELS[3],), fontsize=16)
    ax[3].spines['bottom'].set_color('white')
    fig.subplots_adjust(right=1.2)
    plt.subplots_adjust(wspace=0)
    plt.show()


def plaus_space_decreased(plaus_space, new_plaus_space):
    if len(plaus_space) == 0:
        return True  # to initiate first wave
    for d in range(DIMENSIONS):
        old = [x[d] for x in plaus_space]
        new = [x[d] for x in new_plaus_space]
        if min(old) < min(new) or max(old) > max(new):
            return True
    return False


def run_waves(load_timestamp=None):
    # initialise HM
    hm.sim_func = run_sim_and_get_density
    hm.error_func = calculate_error
    hm.k = 30
    hm.ensemble_samples = 2  # NOTE: should be higher (3 or 4) but keeping low for testing
    # overwrite the hm multiprocessing functions (jupedsim already does multiprocessing)
    hm.variety_func = variety_func
    hm.ensemble_func = ensemble_func
    # create results folder
    global results_dir
    global results
    if load_timestamp != None:
        results = load_results(load_timestamp)
        results_dir = 'results/full_results/%s' % load_timestamp
        wave_no = len(results) + 1
        new_plaus_space = [results[-1]['plaus_space'][i]
                           for i in range(len(results[-1]['plaus_space']))
                           if results[-1]['implaus_scores'][i] < 3]
    else:
        results_dir = 'results/full_results/%s' % strftime('%y%m%d_%H%M%S')
        os.mkdir(results_dir)
        # initialise first wave
        wave_no = 1
        new_plaus_space = init_sample()
    plaus_space = []
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
        uncert, new_plaus_space, implaus_scores = hm.wave(plaus_space)
        results.append({'wave_no': wave_no,
                        'uncert': uncert,
                        'plaus_space': plaus_space,
                        'implaus_scores': implaus_scores,
                        'zone_no': zone_no})
        print(results[-1])
        wave_no += 1
        print(len(new_plaus_space))
        #plot_wave(results[-1])
        # save results at each iteration so they can be examined during runtime
        save_results(results_dir[-13:])


if __name__ == '__main__':
    #run_waves()
    # Using the data with limited pedestrians
    z1_results = load_results('211208_151221')
    z2_results = load_results('220110_134905')
    z3_results = load_results('220117_104155')
    # Using the model to get "true" data:
    # z1_results = load_results('211203_145134')
    # z2_results = load_results('211206_103527')
    # z3_results = load_results('220119_151812')
    idx = -1
    plot_zones_parallel((z1_results[idx], z2_results[idx], z3_results[idx]), exclude_implaus=True)
