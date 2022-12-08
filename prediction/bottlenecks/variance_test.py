""" Measure ensemble variance across 200 runs. """

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import run


SAMPLES = 100

exp_id = 'runs_110_120'
x = (2, 0.2, 1.34, 1, 0.02)

Y = np.empty(SAMPLES)
for i in range(SAMPLES):
    Y[i] = run.run_sim_and_get_time(x, '%s_ini.xml' % exp_id, results_subdir='variance_test')
print(Y)



V = [np.var(Y[:n]) for n in range(3, SAMPLES)]
plt.plot(range(3, SAMPLES), V)
print(V[47])
plt.show()
