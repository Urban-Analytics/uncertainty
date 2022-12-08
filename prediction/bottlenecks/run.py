import os
import subprocess
import pandas as pd
import xml.etree.ElementTree as ET
from time import strftime, time


# NOTE: JPSCORE must be set as an environmental variable
#       pointing to the executable


MAX_FRAMES = 960
FPS = 8


def change_config_core(force_ped_a=5, force_ped_D=0.2, v0_mu=1.34,
                       force_wall_a=5, force_wall_D=0.02,
                       ini_filename='core_ini.xml', results_subdir=None):
    timestamp = strftime('%y%m%d_%H%M%S')
    mytree = ET.parse('config_files/%s' % ini_filename)
    Xoutput_path = mytree.find('header').find('output')
    if results_subdir == None:
        results_subdir = ini_filename[:12]
    Xoutput_path.attrib['path'] = 'results/%s/%s' % (results_subdir, timestamp)

    Xmodel = mytree.find('operational_models').find('model')

    Xforce_ped = Xmodel.find('model_parameters').find('force_ped')
    Xforce_ped.attrib['a'] = str(force_ped_a)
    Xforce_ped.attrib['D'] = str(force_ped_D)

    Xforce_ped = Xmodel.find('model_parameters').find('force_wall')
    Xforce_ped.attrib['a'] = str(force_wall_a)
    Xforce_ped.attrib['D'] = str(force_wall_D)

    Xv0 = Xmodel.find('agent_parameters').find('v0')
    Xv0.attrib['mu'] = str(v0_mu)

    mytree.write(ini_filename)
    return timestamp


def run(X, ini_filename, results_subdir=None):
    """ Run the model with ini filename. """
    print('Simulation starting...')
    timestamp = change_config_core(X[0], X[1], X[2], X[3], X[4], ini_filename, results_subdir)
    subprocess.call('$JPSCORE %s' % ini_filename, shell=True)#, stdout=subprocess.DEVNULL)
    # Jupedsim makes copy of ini file. Delete it.
    os.system('rm %s' % (ini_filename))
    print('...simulation finished.')
    return timestamp


def run_sim_and_get_time(x, ini_filename, results_subdir):
    """ Run Jupedsim core upto 3 attempts to get a non 120 second run. """
    attempts = 1
    frame_no = MAX_FRAMES
    exp_id = ini_filename[:12]
    while attempts < 5 and frame_no == MAX_FRAMES:
        if attempts > 1:
            # remove failed attempt unless it's the last one
            os.system('rm -rf results/%s/%s' % (results_subdir, timestamp))
        timestamp = run(x, ini_filename, results_subdir)
        try:
            fp = 'results/%s/%s/%s_traj.txt' % (results_subdir, timestamp, exp_id)
            traj = pd.read_csv(fp, sep='\t', skiprows=12)
            frame_no = max(traj['FR'])  # get max frame number
        except pd.errors.EmptyDataError:
            frame_no = MAX_FRAMES
        attempts += 1
    return frame_no / FPS


run((5, 0.2, 1.34, 5, 0.02), 'runs_030_040_ini.xml', 'test')
