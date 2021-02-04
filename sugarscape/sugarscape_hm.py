import numpy as np
from itertools import product
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from time import strftime, time

from sugarscape_cg.model import SugarscapeCg

import history_matching


nodes = [0, 3, 3, np.inf]
colors = ['lightskyblue', 'lightskyblue', 'lightgoldenrodyellow', 'lightgoldenrodyellow']
cmap = LinearSegmentedColormap.from_list("", list(zip(nodes, colors)))


def run_simulation(x):
    SS = SugarscapeCg(max_metabolism=x[0], max_vision=x[1])
    #SS = SugarscapeCg(max_metabolism=x)
    SS.verbose = False
    y =  SS.run_model(step_count=50)
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


def plot_implaus_2d(plaus_space, implaus_scores, labels=None):
    plt.clf()
    X1 = sorted(list(set([x[0] for x in plaus_space])))
    X2 = sorted(list(set([x[1] for x in plaus_space])))
    Z = np.empty((len(X1), len(X2)))
    for i1 in range(len(X1)):
        for i2 in range(len(X2)):
            x1 = X1[i1]
            x2 = X2[i2]
            try:
                Z[i1][i2] =min(3, implaus_scores[plaus_space.index((x1, x2))]) 
            except ValueError:
                # unexplored implausible space
                Z[i1][i2] = 3
    #implaus_scores = np.array([min(imp, 3) for imp in implaus_scores])
    #implaus_scores = implaus_scores.reshape(len(X2), len(X1))
    im = plt.imshow(Z, cmap='pink_r', norm=Normalize(0, 3))
    plt.yticks((0, len(X1)-1), (X1[0], X1[-1]))
    plt.xticks((0, len(X2)-1), (X2[0], X2[-1]))
    plt.colorbar(im)
    if labels:
        plt.xlabel(labels[0])
        plt.ylabel(labels[1])
    plt.savefig(strftime('hm_%Y%m%d_%H%M%S.pdf'))
    plt.show()


def example_2d():
    history_matching.y = 63
    history_matching.f = run_simulation
    plaus_metabolism = range(1, 7)
    plaus_vision = range(1, 11)
    plaus_space = []  # not yet explored
    new_plaus_space = list(product(plaus_metabolism, plaus_vision))
    while not history_matching.is_all_plausible(plaus_space, new_plaus_space):
        plaus_space = new_plaus_space
        new_plaus_space, implaus_scores = history_matching.wave(plaus_space)
        plot_implaus_2d(plaus_space, implaus_scores, ('vision','metabolism'))


if __name__ == '__main__':
    example_2d()
