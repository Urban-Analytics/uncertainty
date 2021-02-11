""" Analyse the trend of HM waves to choose a suitable stopping criteria. """

import pickle
import matplotlib.pyplot as plt
import numpy as np

# load history matching results
f = '210124_100055'
with open('results/%s/hm.pkl' % f, 'rb') as pf:
    results = pickle.load(pf)
total_waves = len(results)

def uncertainties():
    """ Fetch the total uncertainties at each wave. """
    return [wave['uncert'] for wave in results]


def implausibility_var():
    """ Fetch the variance of the implausibility scores at each wave. """
    return [np.var(wave['implaus_scores']) for wave in results]


def rectangle_area():
    """ Fetch the area of the non-implausible space found at each wave. """
    Y = []
    for wave in results:
        d0 = []
        d1 = []
        for i in range(len(wave['implaus_scores'])):
            if wave['implaus_scores'][i] < 3:
                d0.append(wave['plaus_space'][i][0])
                d1.append(wave['plaus_space'][i][1])
        area = (max(d0) - min(d0)) * (max(d1) - min(d1))
        Y.append(area)
    return Y

fig, axs = plt.subplots(3, sharex='col')
funcs = (uncertainties, implausibility_var, rectangle_area)
for i in range(3):
    Y = funcs[i]()
    axs[i].plot(range(total_waves), Y)
    axs[i].set_ylabel(funcs[i].__name__)
plt.xticks(range(0, total_waves), range(1, total_waves+1))
plt.xlabel('wave')
plt.show()
