import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


results_dir = 'model/results/farm-ensembles-'

OUTPUTS = ('n small', 'n medium', 'n large')
observations = pd.read_csv('model/farm-size-year.csv')
YEARS = range(13)
TOTAL_YEARS = 13

# Drivers are in the order given in figure 10 of the paper:
# Ge, J. et al. Not one Brexit
# How local context and social processes influence policy analysis
# PloS one, Public Library of Science
# San Francisco, CA USA, 2018, 13, e0208451
drivers = (
          (False, False, False, False), (False, False, False, True),
          (False, False, True, True), (False, False, True, False),
          (False, True, False, True), (False, True, False, False),
          (False, True, True, True), (False, True, True, False),
          (True, False, False, True), (True, False, False, False),
          (True, False, True, True), (True, False, True, False),
          (True, True, False, True), (True, True, False, False),
          (True, True, True, True), (True, True, True, False)
          )


def get_fp(driver, i=1):
    # Get the filepath of a driver
    # If no index is given then get first run
    fp = results_dir
    fp = fp + 'true-' if driver[0] else fp + 'false-'
    fp = fp + 'true-' if driver[1] else fp + 'false-'
    fp = fp + 'true-' if driver[2] else fp + 'false-'
    fp = fp + 'true-' if driver[3] else fp + 'false-'
    return fp + str(i) + '.csv'


def driver_name(driver):
    """ Return string describing the given driver."""
    s = ''
    s = s + 'succession ' if driver[0] else s
    s = s + 'leisure ' if driver[1] else s
    s = s + 'diversification ' if driver[2] else s
    s = s + 'industrialisation' if driver[3] else s
    if s == '':
        return 'profit drivern'
    return s


def percentage_error(observations_output, estimates_output):
    result = 0
    for year in YEARS:
        obs = observations_output[year]
        est = estimates_output[year]
        result += abs((obs - est) / obs) * 100
    return result / len(YEARS)


def mean_absolute_error(observations_output, estimates_output):
    return np.mean([abs(observations_output[year] - estimates_output[year])
                    for year in YEARS])


def mean_absolute_scaled_error(observations_output, estimates_output):
    """ The observation and estimate must be of a single output."""
    result = 0
    mae = mean_absolute_error(observations_output, estimates_output)
    scale = sum([abs(observations_output[year] - observations_output[year-1])
                 for year in YEARS[1:]]) / (TOTAL_YEARS - 1)
    return mae / scale


def plot_simulation_results():
    """ Plot the simulation results from a single run for each driver."""
    fig, axs = plt.subplots(16, 3, figsize=(8, 8))
    for driver_i in range(len(drivers)):
        fp = get_fp(drivers[driver_i])
        df = pd.read_csv(fp)
        for output_i in range(3):
            Y = df[OUTPUTS[output_i]].tolist()
            Y_obs = observations[OUTPUTS[output_i]].tolist()
            axs[driver_i][output_i].plot(range(13), Y, c='r')
            axs[driver_i][output_i].plot(range(13), Y_obs, c='k')
            axs[driver_i][output_i].set_ylim(min(min(Y), min(Y_obs)),
                                max(max(Y), max(Y_obs)))
    plt.show()


def plot_ensemble_results(driver):
    fig, axs = plt.subplots(1, 3)
    fp = get_fp(driver)
    for output_i in range(3):
        Y_obs = observations[OUTPUTS[output_i]].tolist()
        axs[output_i].plot(range(13), Y_obs, c='k')
    for output_i in range(3):
        Y_min = [np.inf for year in range(13)]
        Y_max = [-np.inf for year in range(13)]
        for i in range(k):
            df = pd.read_csv(get_fp(driver)[:-5] + str(i+1) + '.csv')
            Y = df[OUTPUTS[output_i]].tolist()
            for year in range(13):
                Y_min[year] = min(Y_min[year], Y[year])
                Y_max[year] = max(Y_max[year], Y[year])
        axs[output_i].plot(range(13), Y_min, c='r')
        axs[output_i].plot(range(13), Y_max, c='r')
    #axs[output_i].set_ylim(min(min(Y), min(Y_obs)),
    #                    max(max(Y), max(Y_obs)))
    fig.suptitle(driver_name(driver))
    plt.show()


# choose an error function to compare a simulation against the observation
error_func = mean_absolute_scaled_error
