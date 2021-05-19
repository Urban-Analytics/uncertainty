""" Read the activations (entry/exit time and location) over a 2.638 minute period."""

import csv
import matplotlib.pyplot as plt
import numpy as np

TOTAL_GATES = 11
FPS = 25


times_in = []
path_totals = [[0 for i in range(TOTAL_GATES)] for j in range(TOTAL_GATES)]
entry_totals = [0 for i in range(TOTAL_GATES)]
min_time = np.inf
max_time = -np.inf

with open('activation.dat') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ')
    next(reader, None)  # skip header
    for row in reader:
        time_in = float(row[1])
        min_time = min(min_time, time_in)
        max_time = max(max_time, time_in)
        gate_in = int(row[2])
        gate_out = int(row[3])
        times_in.append((time_in / FPS, gate_in))
        path_totals[gate_in][gate_out] += 1
        # entry_totals is not memory efficient (can derive from path_totals) but easier to code
        entry_totals[gate_in] += 1

total_time = (max_time - min_time) / FPS
from tabulate import tabulate
table = []
i = 0
for entry in range(TOTAL_GATES):
    m = np.mean(path_totals[entry])
    for exit in range(TOTAL_GATES):
        if path_totals[entry][exit] > m:
            time_interval = int(round(total_time / path_totals[entry][exit]))
            table.append([i, entry, exit, path_totals[entry][exit], time_interval])
            #if i in (0,1,3,4,5,6,8,9,23,24,25,26,27,28,30):
            #    table.append([i, time_interval])
            i += 1
print(tabulate(table))

# create groups
rooms = ['x_min="0" x_max="5" y_min="10" y_max="30"',
         'x_min="0" x_max="18" y_min="45" y_max="50"',
         'x_min="32" x_max="50" y_min="45" y_max="50"',
         'x_min="47" x_max="53" y_min="43" y_max="50"',
         'x_min="47" x_max="53" y_min="30" y_max="39"',
         'x_min="47" x_max="53" y_min="14" y_max="25"',
         'x_min="47" x_max="53" y_min="0" y_max="8"',
         'x_min="39.75" x_max="53" y_min="0" y_max="5"',
         'x_min="26.5" x_max="39.75" y_min="0" y_max="5"',
         'x_min="13.25" x_max="26.5" y_min="0" y_max="5"',
         'x_min="0" x_max="13.25" y_min="0" y_max="5"']
for row in table:
    i, entry, exit, total, time = row
    # print(f'<group group_id="%d" agent_parameter_id="1" room_id="0" subroom_id="0"\
    #       number="0" goal_id="%d" router_id="1" %s />' % (i, exit, rooms[entry]))
    # time must be an int
    time_min = 0
    total_time = int(round(total_time))
    if time == total_time:
        time_min = np.random.randint(0, total_time)
    print(f'<source id="%d" group_id="%d" frequency="%d" \
          N_create="%d" time_min="%d" agents_max="100" %s />' % (i, i, time, 1, time_min, rooms[entry]))
