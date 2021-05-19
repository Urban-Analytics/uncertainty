import os
import subprocess
import xml.etree.ElementTree as ET
from time import strftime, time


# NOTE: JPSCORE, JPSREPORT and JPSVIS must be set as environmental variables
#       pointing to the executable

#NOTE will have to change how this is done if more parameters are added
# could pass xml of things to change
def change_config_core(force_ped, force_wall):
    timestamp = strftime('%y%m%d_%H%M%S')
    # Update core file
    mytree = ET.parse('core_ini.xml')
    Xoutput_path = mytree.find('header').find('output')
    Xoutput_path.attrib['path'] = 'results/run_results_%s' % timestamp
    Xmodel_params = mytree.find('operational_models').find('model').find('model_parameters')
    Xforce_ped = Xmodel_params.find('force_ped')
    Xforce_wall = Xmodel_params.find('force_wall')
    Xforce_ped.attrib['a'] = force_ped['a']
    Xforce_ped.attrib['D'] = force_ped['D']
    Xforce_wall.attrib['a'] = force_wall['a']
    Xforce_wall.attrib['D'] = force_wall['D']
    mytree.write('core_ini.xml')
    return timestamp


def change_config_report(timestamp):
    # Update report file
    mytree = ET.parse('report_ini.xml')
    Xoutput = mytree.find('output')
    Xoutput.attrib['location'] = 'results/report_results_%s' % timestamp
    Xoutput = mytree.find('trajectories').find('path')
    Xoutput.attrib['location'] = './results/run_results_%s' % timestamp
    mytree.write('report_ini.xml')


def run():
    print('Simulation starting...')
    subprocess.call('$JPSCORE core_ini.xml', shell=True, stdout=subprocess.DEVNULL)
    print('...simulation finished.')


def report():
    print('Reporting starting...')
    subprocess.call('$JPSREPORT report_ini.xml', shell=True, stdout=subprocess.DEVNULL)
    print('...reporting finished.')


def vis():
    subprocess.call('$JPSVIS results/traj.xml', shell=True, stdout=subprocess.DEVNULL)


def run_with_change(force_ped, force_wall):
    timestamp = change_config(force_ped, force_wall)
    run()
    return timestamp
