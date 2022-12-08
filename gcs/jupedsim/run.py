import os
import subprocess
import xml.etree.ElementTree as ET
from time import strftime, time


# NOTE: JPSCORE, JPSREPORT and JPSVIS must be set as environmental variables
#       pointing to the executables

#NOTE will have to change how this is done if more parameters are added
# could pass xml of things to change
def change_config_core(force_ped_a=5, force_ped_D=0.2, v0_mu=1.34,
                       force_wall_a=5, force_wall_D=0.02, results_dir='results'):
    # use a timestamp to uniquely identify the parameters
    timestamp = strftime('%y%m%d_%H%M%S')
    mytree = ET.parse('core_ini.xml')
    Xoutput_path = mytree.find('header').find('output')
    Xoutput_path.attrib['path'] = '%s/run_results_%s' % (results_dir, timestamp)

    Xmodel = mytree.find('operational_models').find('model')

    Xforce_ped = Xmodel.find('model_parameters').find('force_ped')
    Xforce_ped.attrib['a'] = str(force_ped_a)
    Xforce_ped.attrib['D'] = str(force_ped_D)

    Xforce_ped = Xmodel.find('model_parameters').find('force_wall')
    Xforce_ped.attrib['a'] = str(force_wall_a)
    Xforce_ped.attrib['D'] = str(force_wall_D)

    Xv0 = Xmodel.find('agent_parameters').find('v0')
    Xv0.attrib['mu'] = str(v0_mu)

    mytree.write('core_ini.xml')
    return timestamp


def update_core_timestamp(results_dir='results'):
    # use a timestamp to uniquely identify the parameters
    timestamp = strftime('%y%m%d_%H%M%S')
    mytree = ET.parse('core_ini.xml')
    Xoutput_path = mytree.find('header').find('output')
    Xoutput_path.attrib['path'] = '%s/run_results_%s' % (results_dir, timestamp)
    mytree.write('core_ini.xml')
    return timestamp


def change_config_report(timestamp, results_dir='results', config_file='report_ini.xml'):
    """ Use a timestamp to find the model outputs and generate the report. """
    mytree = ET.parse(config_file)
    Xoutput = mytree.find('output')
    Xoutput.attrib['location'] = '%s/report_results_%s' % (results_dir, timestamp)
    Xoutput = mytree.find('trajectories').find('path')
    Xoutput.attrib['location'] = './%s/run_results_%s' % (results_dir, timestamp)
    mytree.write('report_ini.xml')


def run():
    """ Run the model with core_ini.xml. """
    print('Simulation starting...')
    subprocess.call('$JPSCORE core_ini.xml', shell=True, stdout=subprocess.DEVNULL)
    print('...simulation finished.')


def report(config_file='report_ini.xml'):
    """ Run the simulation report with report_ini.xml. """
    print('Reporting starting...')
    subprocess.call('$JPSREPORT %s' % config_file, shell=True, stdout=subprocess.DEVNULL)
    print('...reporting finished.')


def vis(timestamp):
    """ Visualise the run that is assigned the given timestamp. """
    subprocess.call('$JPSVIS results/run_results_%s/traj.xml' % timestamp,
                    shell=True, stdout=subprocess.DEVNULL)


def run_with_change(X, results_dir='results'):
    timestamp = change_config_core(X[0], X[1], X[2], results_dir)
    run()
    return timestamp


if __name__ == '__main__':
    change_config_core(results_dir='results/true')
    run()
    change_config_report('true', results_dir='results/true')
    report()
