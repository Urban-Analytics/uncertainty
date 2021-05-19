import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import helper

# number of ensembles run with results saved
k = 100

# indexes of the plausible models found in history matching
plaus_space = [12, 13, 14, 15]

# each output has an individually measured uncertainty
uncert = {'n small': 1.809, 'n medium': 2.232, 'n large': 5.558}

posteriors = dict((x, 0) for x in plaus_space)
# each possible set of factors is referred to as a "driver"
for driver_i in plaus_space:
    driver = helper.drivers[driver_i]
    for i in range(k):
        # the simulations have been prerun and saved to csv
        df = pd.read_csv(helper.get_fp(driver, i+100))
        passed = True  # assume passed until proven otherwise
        for output in helper.OUTPUTS:
            obs = helper.observations[output].tolist()
            est = df[output].tolist()
            d = helper.error_func(obs, est)  # compute distance
            # if one output fails to pass, the whole simulation has failed
            if d > uncert[output] + 0.5:
                passed = False
                break
        if passed:
            posteriors[driver_i] += 1
print(posteriors)

#fig, ax = plt.subplots(1)
Y = [posteriors[x]/k for x in plaus_space]
print(Y)
plt.bar(plaus_space, Y, color='sandybrown')
plt.xticks(plaus_space, (13, 14, 15, 16), fontsize=14)
plt.yticks((0, 0.25, 0.5, 0.75, 1.0), (0, 0.25, 0.5, 0.75, 1.0), fontsize=14)
plt.ylabel('% accepted runs', fontsize=16)
plt.xlabel('model no.', fontsize=16)
plt.tight_layout()
#fig.subplots_adjust(left=0.15)
plt.show()
