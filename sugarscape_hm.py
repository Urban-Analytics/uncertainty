import numpy as np

from sugarscape_cg.model import SugarscapeCg

import history_matching


def run_simulation(x):
    SS = SugarscapeCg(max_metabolism=x)
    SS.verbose = False
    y =  SS.run_model(step_count=50)
    return y


history_matching.y = 66
history_matching.f = run_simulation

plaus_space = np.array(range(3, 10))
new_plaus_space = history_matching.wave(np.array(plaus_space), True)
while not history_matching.is_all_plausible(plaus_space, new_plaus_space):
    plaus_space = new_plaus_space
    new_plaus_space = history_matching.wave(plaus_space, True)
print('Finished with', str(new_plaus_space))


