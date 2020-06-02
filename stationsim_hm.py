import numpy as np
import matplotlib.pyplot as plt
import math

from sys import path
path.append('/home/josie/Dropbox/Projects/Leeds/DUST/dust-master/Projects/ABM_DA/')
from stationsim.stationsim_model import Model

import history_matching

# goal correctly estimate the amount of time it takes for all agents to leave the environment for a population of 25


# "real world" observation

y_pop_total = 75
y_seed = 1376479047  # from which the observation y was derived


def run(x):
    model = Model(pop_total=y_pop_total, speed_mean=x, do_print=False)
    for _ in range(model.step_limit):
        model.step()
    return model.step_id  # finish time

history_matching.y = 1802
history_matching.f = run

# test different speed_mean
X_test = np.linspace(0.4, 4, 51)
history_matching.wave(X_test, plot=True)
