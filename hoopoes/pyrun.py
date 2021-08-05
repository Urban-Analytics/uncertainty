import os
import pyNetLogo
import multiprocessing as mp

import numpy as np
import matplotlib.pyplot as plt


# Values taken from Thiele et al. 2015
scout_survival = 0.8
criteria = {
    # the long-term mean number of birds
    'abundance': (115, 135),
    # the standard deviation from year to year in the annual number of birds
    'variation': (10, 15),
    #  the average percentage of territories that lack one or both alpha animals
    'vacancies': (15, 30)}

YEARS = 22
MONTHS = 12

modelfile = os.path.abspath('./SM2_Hoopoes.nlogo')  # requires netlogo v5


def initialiser():
    # We need to set the instantiated netlogo
    # link as a global so run_simulation can use it
    global netlogo
    netlogo = pyNetLogo.NetLogoLink(gui=False,
                                    netlogo_home='/home/josie/Downloads/netlogo-5.3.1-64/',
                                    netlogo_version='5')
    netlogo.load_model(modelfile)


def run_simulation(x):
    """ Run the model once with the parameter set.

    Note, initialiser() must be called prior to run_simulation.
    x: parameters as the tuple (scout_prob, survival_prob).
    Returns: (abundance, variation, vacancies)
    """
    # used for plots
    # ~ non_alpha_ages = []
    # ~ foray_ages = []
    total_birds = []
    total_vacancies = []
    netlogo.command('set scout-prob %f' % round(x[0], 2))
    netlogo.command('set survival-prob %f' % round(x[1], 2))
    netlogo.command('set scouting-survival %f' % scout_survival)
    netlogo.command('setup')
    for i in range(MONTHS * YEARS):
        netlogo.command('go')
        if netlogo.report('month') == 12 and netlogo.report('year') > 2:
            total_birds.append(netlogo.report('count turtles'))
            # calculation of vacancies is copied from netlogo file
            total_vacancies.append(netlogo.report(
                        '(count patches * 2) - count turtles with [is-alpha?]'))
            # to replicate the plots
            #non_alpha_ages.append(netlogo.report('mean non-alpha-ages'))
            #foray_ages.append(netlogo.report('mean foray-ages'))
    #foray_months = netlogo.report('foray-months')
    #plt.hist(foray_months, bins=(range(1, 14)))
    #group_sizes = netlogo.report('group-sizes')
    #plt.hist(group_sizes, bins=(range(1, 12)))
    #plt.plot(range(YEARS-2), non_alpha_ages, c='k')
    #plt.plot(range(YEARS-2), foray_ages, c='r')
    #plt.show()
    #c1_passed  = within_range('abundance', np.mean(total_birds))
    #c2_passed = within_range('variation', np.std(total_birds, ddof=1))
    #c3_passed = within_range('vacancies', np.mean(total_vacancies))
    netlogo.kill_workspace()
    return(np.mean(total_birds),
           np.std(total_birds, ddof=1),
           np.mean(total_vacancies))


def error(results):
    """ Calculate the error (cost) of the output.

    results: tuple of (abundance, variation, vacancies)
    Returns: float error measurement
    """
    def within_range(criterion, value):
        return criteria[criterion][0] <= value <= criteria[criterion][1]
    # actual results
    abundance, variation, vacancies = results
    # expected results
    abundance_m = np.mean(criteria['abundance'])
    variation_m = np.mean(criteria['variation'])
    vacancies_m = np.mean(criteria['vacancies'])
    # calculate cost
    abundance_e = (0 if within_range('abundance', abundance)
                   else ((abundance_m - abundance) / abundance_m)**2)
    variation_e = (0 if within_range('variation', variation)
                   else ((variation_m - variation) / variation_m)**2)
    vacancies_e = (0 if within_range('vacancies', vacancies)
                   else ((vacancies_m - vacancies) / vacancies_m)**2)
    return abundance_e + variation_e + vacancies_e


def run_ensembles(X, k):
    """ Run a list of parameter sets X a total of k times.

    x: parameters
    k: total runs
    Returns: a list of all run results
    """
    all_sample_results = []
    for x in X:
        single_sample_results = []
        with mp.Pool(mp.cpu_count(), initializer=initialiser) as executor:
            for entry in executor.map(run_simulation, [x for _ in range(k)]):
                single_sample_results.append(entry)
        all_sample_results.append(single_sample_results)
    return all_sample_results


def run_varieties(X):
    """ Run a list of parameter sets X, each run only once.

    X: list of parameter sets
    Returns: Ordered list of results of X
        """
    results = []
    with mp.Pool(mp.cpu_count(), initializer=initialiser) as executor:
        for entry in executor.map(run_simulation, X):
            results.append(entry)
    return results


def run_solo(x):
    """ Run a single instance with the parameters x.

    x = (scout_prob, survival_prob)
    """
    initialiser()
    return run_simulation(x)


if __name__ == '__main__':
    results = []
    with mp.Pool(mp.cpu_count(), initializer=initialiser) as executor:
        for entry in executor.map(run_simulation, [[0.3, 0.98], [0.2, 0.95]]):
                results.append(entry)
    print(results)
    print(error(results[0]))
    print(error(results[1]))
