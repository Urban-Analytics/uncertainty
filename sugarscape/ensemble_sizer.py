import matplotlib.pyplot as plt
import multiprocessing as mp
import numpy as np

from sugarscape_cg.model import SugarscapeCg

# Tested parameters are
# (1 1), (2, 10), and (4, 7)
x = (2, 10)  # currently testing

#K = [2**i for i in range(2, 9)]

# Results:
Y_1_1  = [9.5, 12.0, 9.495402298850575, 13.472033898305085, 12.902496878901374, 13.87983193277311, 12.064250559284115, 12.899162011173186, 12.997488584474885, 14.859180722891567, 15.592818740399387, 14.5289591815429, 13.399783099080338, 14.578253863619718, 15.18590852130326, 14.131669106087712, 12.323690442360519]
Y_2_10 = [11.299999999999999, 6.123809523809525, 12.878160919540228, 12.541242937853106, 12.98377028714107, 12.137535014005605, 13.808545861297539, 11.612011173184356, 12.047239518472393, 12.636530120481929, 12.291743471582183, 12.822006472491909, 13.373893805309734, 13.698557093679044, 12.755482456140351, 13.85396541443053, 14.21083641185943]
Y_4_7 = [16.5, 22.599999999999998, 10.217241379310343, 20.937853107344633, 22.774157303370785, 17.024929971988797, 16.290827740492173, 18.067380509000618, 18.340390203403903, 17.881124497991966, 17.512544802867385, 19.954327174026517, 19.333194516744754, 18.373661466344394, 18.864135338345864, 18.55706076868868, 18.695931609358723]

K = [5, 15, 30, 60, 90, 120, 150, 180, 220, 250, 280, 310, 340, 370, 400, 430, 460]


def run_simulation(_):
    SS = SugarscapeCg(max_metabolism=x[0], max_vision=x[1])
    SS.verbose = False
    y =  SS.run_model(step_count=30)
    return y


def run_ensemble(k):
    """ Run the model with x k times. """
    pool = mp.Pool(mp.cpu_count())
    results = pool.map_async(run_simulation, range(k))
    pool.close()
    return results.get()


def get_results_of_x():
    """ Measure ensemble variance of x across all ensemble sizes in K. """
    Y = []
    for k in K:
        results = run_ensemble(k)
        Y.append(np.var(results, ddof=1))
    print(Y)
    plt.plot(K, Y)
    plt.show()

def plot_all_results():
    """ Plot results using the saved values from previous runs. """
    Y = (Y_1_1, Y_4_7, Y_2_10)
    style = ('-', '--', '-.')
    for i in range(3):
        plt.plot(K, Y[i], linestyle=style[i])
    plt.xlabel('ensemble size')
    plt.ylabel('ensemble variance')
    plt.show()


plot_all_results()
