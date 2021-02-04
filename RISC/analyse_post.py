import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import helper

# number of ensembles run with results saved
k = 30

# indexes of the plausible models found in history matching
plaus_space = [12, 13, 14, 15]

# each output has an individually measured uncertainty
uncert = {'n small': 1.473, 'n medium': 2.184, 'n large': 5.588}

posteriors = dict((x, 0) for x in plaus_space)
# each possible set of factors is referred to as a "driver"
for driver_i in plaus_space:
    driver = helper.drivers[driver_i]
    for i in range(k):
        # the simulations have been prerun and saved to csv
        df = pd.read_csv(helper.get_fp(driver)[:-5] + str(i+1) + '.csv')
        passed = True  # assume passed until proven otherwise
        for output in helper.OUTPUTS:
            obs = helper.observations[output].tolist()
            est = df[output].tolist()
            d = helper.error_func(obs, est)  # compute distance
            # if one output fails to pass, the whole simulation has failed
            if d > uncert[output] * 1.2:
                passed = False
                break
        if passed:
            posteriors[driver_i] += 1
print(posteriors)

Y = [posteriors[x]/30 for x in plaus_space]
plt.bar(plaus_space, Y, color='sandybrown')
plt.xticks(plaus_space)
plt.xlabel('model no.')
plt.ylabel('% accepted runs')
plt.show()
