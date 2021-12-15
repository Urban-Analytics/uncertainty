import os
import tempfile
import numpy as np
import pyabc
import pickle
from time import strftime
import matplotlib.pyplot as plt

import pyrun

# Let ID be the test ID  (or timestamp) of the history matching run
# that the prior is based on.
id = 'results/210125_151327'


def model(x):
    y = pyrun.run_solo((x['scout_prob'], x['survival_prob']))
    return {'y': y}

def distance(result, data):
    # data is 0
    return pyrun.error(result['y'])

def priors(scout_prob_range, survival_prob_range):
    prior = pyabc.Distribution(scout_prob=pyabc.RV("uniform",
                                                   scout_prob_range[0],
                                                   scout_prob_range[1]-scout_prob_range[0]),
                               survival_prob=pyabc.RV("uniform",
                                                      survival_prob_range[0],
                                                      survival_prob_range[1]-survival_prob_range[0]))
    return prior


def run(scout_prob_range=(0, 0.5), survival_prob_range=(0.95, 1), filename_suffix=''):
    # uniform distribution is given as (start, width) and NOT (start, end)
    prior = priors(scout_prob_range, survival_prob_range)

    abc = pyabc.ABCSMC(model, prior, distance)

    #TOOD: for the future you might want to add a check to see if the db already
    # exists so you can load it
    # directory is current directory plus id
    db_dir = os.path.dirname(os.path.realpath(__file__)) + '/' + id
    db_filename = 'pyabc_results%s.db' % filename_suffix
    db_path = pyabc.create_sqlite_db_id(dir_=db_dir, file_=db_filename)
    abc.new(db_path)
    history = abc.run()


def plot(scout_prob_range=(0, 0.5), survival_prob_range=(0.95, 1), filename_suffix=''):
    db_dir = os.path.dirname(os.path.realpath(__file__)) + '/' + id
    db_filename = 'pyabc_results%s.db' % filename_suffix
    db_path = pyabc.create_sqlite_db_id(dir_=db_dir, file_=db_filename)
    prior = priors(scout_prob_range, survival_prob_range)
    abc = pyabc.ABCSMC(model, prior, distance)
    history = abc.load(db_path, 1)
    df, w = history.get_distribution(m=0, t=history.max_t)
    # plot posterior
    fig, ax = plt.subplots()
    pyabc.visualization.plot_kde_2d(
        df, w, x="scout_prob", y="survival_prob",
        xmin=0, xmax=0.5, ymin=0.95, ymax=1,
        ax=ax, cmap='magma')
    plt.xlabel('scouting probability', fontsize=16)
    plt.ylabel('survival probability', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    #plt.show()
    plt.savefig('%s/abc_posterior%s.pdf' % (id, filename_suffix))
    plt.close()

    # # Plot sampling info.
    # _, arr_ax = plt.subplots(3)
    # pyabc.visualization.plot_sample_numbers(history, ax=arr_ax[0])
    # pyabc.visualization.plot_epsilons(history, ax=arr_ax[1])
    # pyabc.visualization.plot_effective_sample_sizes(history, ax=arr_ax[2])
    # plt.gcf().tight_layout()
    # #plt.show()
    # plt.savefig('%s/abc_analysis%s.pdf' % (id, filename_suffix))


if __name__ == '__main__':
    history = run()
    plot()
