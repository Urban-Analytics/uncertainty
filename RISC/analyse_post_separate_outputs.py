import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import helper

# number of ensembles run with results saved
k = 10
# drivers to be ploted (as indexed in helper.drivers)
driver_indexes = range(16)
thresholds = np.linspace(0, 50, 201)

# to automatically reconfigure plots if not showing all 16 drivers
total_drivers = len(driver_indexes)
start = 12

colours = ('darkorange', 'maroon', 'maroon', 'darkorange',
           'darkorange', 'darkorange', 'darkorange', 'darkorange',
           'indianred', 'indianred', 'indianred', 'indianred',
           'limegreen', 'limegreen', 'limegreen', 'limegreen')
col_labels = ['n small', 'n medium', 'n large']


def get_post(driver_i):
    post = [dict((output, 0) for output in helper.OUTPUTS)
            for t in range(len(thresholds))]
    driver = helper.drivers[driver_i]
    for i in range(k):
        df = pd.read_csv(helper.get_fp(driver)[:-5] + str(i+1) + '.csv')
        for output in helper.OUTPUTS:
            obs = helper.observations[output].tolist()
            est = df[output].tolist()
            d = helper.error_func(obs, est)  # compute distance
            for thresh_i in range(len(thresholds)):
                if d < thresholds[thresh_i]:
                    post[thresh_i][output] += 1/k  # 1/k to get percentage
    return post


fig, axs = plt.subplots(total_drivers-start, 3, figsize=(8, 8), sharex='col', sharey='row')
for driver_i in driver_indexes[start:]:
    post = get_post(driver_i)
    for output in range(len(helper.OUTPUTS)):
        axs[driver_i-start][output].plot(thresholds,
                                   [post[t][helper.OUTPUTS[output]]
                                    for t in range(len(thresholds))],
                                    linewidth=2,
                                    color=colours[driver_i])
        axs[driver_i-start][output].spines['top'].set_color('white')
        axs[driver_i-start][output].spines['right'].set_color('white')


plt.subplots_adjust(left=0.2, hspace=0.4)
for ax, col in zip(axs[0], range(3)):
    ax.set_title(col_labels[col])
for ax, col in zip(axs[-1], range(3)):
    ax.set_xlabel('threshold')
    if col == 0:
        ax.set_xticks(range(0, 4))
        ax.set_xlim(0, 3)
    elif col == 1:
        ax.set_xticks(range(0, 4))
        ax.set_xlim(0, 3)
    else:
        ax.set_xticks(range(0, 11, 5))
        ax.set_xlim(0, 10)
for ax, row in zip(axs[:,0], range(total_drivers)):
    ax.set_ylabel('Model ' + str(row+start+1), rotation=0, size='medium', labelpad=60)
plt.show()
