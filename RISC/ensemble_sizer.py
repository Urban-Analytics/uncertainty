import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import helper

smallest = 3
k = 100



fig, axs = plt.subplots(1, 3, figsize=(11,4))
ax_index = 0
for output in helper.OUTPUTS:
    obs = helper.observations[output].tolist()
    axs[ax_index].set_title(output, fontsize=16)
    for driver in helper.drivers:
        # get error of each run
        errors = []
        for i in range(k):
            df = pd.read_csv(helper.get_fp(driver)[:-5] + str(i+1) + '.csv')
            errors.append(helper.error_func(obs, df[output]))
        # get variances
        vars = [np.var(errors[:i], ddof=1) for i in range(smallest, k+1)]
        axs[ax_index].plot(range(smallest, k+1), vars)
        axs[ax_index].set_xlabel('ensemble size', fontsize=15)
        axs[ax_index].tick_params(axis='x', labelsize=14)
        axs[ax_index].tick_params(axis='y', labelsize=14)
    ax_index += 1


axs[0].set_ylabel('ensemble variance', fontsize=15)
fig.tight_layout()
plt.show()
