""" Observe how ensemble variance changes in accordance with ensemble size. """

import numpy as np
import matplotlib.pyplot as plt
import csv

import pyrun
import hoopoes_hm as hm

# filepath for results
filepath = 'results/ensemble_sizer_results.csv'

# How many random samples to test
total_samples = 50
# Set the list of ensemble sizes to test
K = [2**i for i in range(2, 7)]


def run_ensembles():
    """ Run the total samples k times for each k in K.

    Saves the ensemble variance for each sample for each k. """
    # Sample from the space
    hm.samples = total_samples
    X = hm.init_sample()
    # Run each sample x a total of k times for each k in K and plot the variance
    with open(filepath, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['scout_prob', 'scout_survival'] + K)
        for x in X:
            V = [x[0], x[1]]
            for k in K:
                run_results = pyrun.run_ensemble(x, k)
                errors = [pyrun.error(r) for r in run_results]
                V.append(np.var(errors, ddof=1))
            writer.writerow(V)


def plot_ensemble_variances():
    """ Plot the ensemble variance over K for each sample from saved csv. """
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            Y = [float(r) for r in row[2:]]
            plt.plot(K, Y)
    plt.xlabel('Total runs')
    plt.ylabel('Ensemble variance')
    plt.show()

if __name__ == '__main__':
    #run_ensembles()
    plot_ensemble_variances()
