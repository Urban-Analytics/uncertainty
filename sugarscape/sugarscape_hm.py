import os, sys
import numpy as np
from itertools import product
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from time import strftime, time
import os
import pickle

from sugarscape_cg.model import SugarscapeCg

# import history_matching from parent directory
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import history_matching

results = []

nodes = [0, 1, 1, 1]
colors = ['sandybrown', 'sandybrown', 'dimgrey', 'dimgrey']
cmap = LinearSegmentedColormap.from_list("", list(zip(nodes, colors)))


def run_simulation(x):
    SS = SugarscapeCg(max_metabolism=x[0], max_vision=x[1])
    SS.verbose = False
    y =  SS.run_model(step_count=30)
    return y


def plot_implaus_1d(X, implaus_scores):
    plt.clf()
    for i in range(len(X)):
        if implaus_scores[i] < 3:
            c = u'#1f77b4'
        else:
            c = u'#ff7f0e'
        plt.scatter(X[i], implaus_scores[i], color=c)
    plt.axhline(y=3, xmin=0, xmax=1)
    plt.xlim(min(X), max(X))
    plt.show()

def plot_wave(wave, show=True):
    plt.clf()
    plaus_space = wave['plaus_space']
    implaus_scores = wave['implaus_scores']
    X2 = range(1, 17)
    X1 = range(1, 5)
    Z = np.empty((len(X1), len(X2)))
    for i1 in range(len(X1)):
        for i2 in range(len(X2)):
            x1 = X1[i1]
            x2 = X2[i2]
            try:
                if implaus_scores[plaus_space.index((x1, x2))] < 3:
                    Z[i1][i2] = 0
                else:
                    Z[i1][i2] = 3
            except ValueError:
                # unexplored implausible space
                Z[i1][i2] = 3
    im = plt.imshow(Z, cmap=cmap)
    plt.gca().invert_yaxis()
    plt.yticks(range(len(X1)), X1)
    plt.xticks(range(len(X2)), X2)
    plt.xlabel('max vision')
    plt.ylabel('max metabolism')
    plt.subplots_adjust(bottom=0.15)
    if show:
        plt.show()



def plot_saved_results(results_dir, save=False):
    with open('results/%s/hm.pkl' % results_dir, 'rb') as pfile:
        results = pickle.load(pfile)
    for wave in results:
        if save:
            plot_wave(wave, show=False)
            plt.savefig('results/%s/wave_%d.pdf' % (results_dir, wave['wave_no']))
        else:
            plot_wave(wave, show=True)


def save_results(results_dir):
    """ Save results of all waves using pickle. """
    # overwrites save of the previous wave
    filepath = 'results/%s/hm.pkl' % results_dir
    with open(filepath, 'wb') as pfile:
        pickle.dump(results, pfile)


def example_2d():
    results_dir = strftime('%y%m%d_%H%M%S')
    os.mkdir(results_dir)
    wave_no = 1
    obs = 66  # metab 4, vision 6
    history_matching.k = 200
    history_matching.sim_func = run_simulation
    history_matching.error_func = lambda y: abs(y - obs)
    plaus_metabolism = range(1, 5)
    plaus_vision = range(1, 17)
    plaus_space = []  # not yet explored
    new_plaus_space = list(product(plaus_metabolism, plaus_vision))
    while not history_matching.is_all_plausible(plaus_space, new_plaus_space):
        plaus_space = new_plaus_space
        print(len(new_plaus_space))
        print(new_plaus_space)
        uncert, new_plaus_space, implaus_scores = history_matching.wave(plaus_space)
        results.append({'wave_no': wave_no,
                        'uncert': uncert,
                        'plaus_space': plaus_space,
                        'implaus_scores': implaus_scores})
        wave_no += 1
        save_results(results_dir)
        #plot_wave(results[-1])


if __name__ == '__main__':
    #example_2d()
    #plot_saved_results('210205_160332', save=False)
    plot_saved_results('210209_134031', save=True)
