""" Run the netlogo model."""

import os
import pyNetLogo
import multiprocessing as mp


#change as required
NETLOGO_HOME = os.environ['HOME'] + '/Downloads/NetLogo 6.1.1/'
NETLOGO_VERSION = '6.1'

drivers = ((False, False, False, False), (False, False, False, True),
           (False, False, True, True), (False, False, True, False),
           (False, True, False, True), (False, True, False, False),
           (False, True, True, True), (False, True, True, False),
           (True, False, False, True), (True, False, False, False),
           (True, False, True, True), (True, False, True, False),
           (True, True, False, True), (True, True, False, False),
           (True, True, True, True), (True, True, True, False)
          )

drivers = ((False, False, False, False),)

modelfile = os.path.abspath('./model/RISC_BREXIT_20180209_run.nlogo')


def initialiser():
    # we need to set the instantiated netlogo
    # link as a global so run_simulation can use it
    global netlogo
    netlogo = pyNetLogo.NetLogoLink(gui=False,
                                    netlogo_home=NETLOGO_HOME,
                                    netlogo_version=NETLOGO_VERSION)
    netlogo.load_model(modelfile)
    netlogo.command('set scenario "S0 no brexit"')
    netlogo.command('set range-tourism 10')
    netlogo.command('set range-manager 15')
    netlogo.command('set min-size-manager 50')
    netlogo.command('set annual-rate-succession-issue 0.01')
    netlogo.command('set rate-expand 0.05')
    netlogo.command('set rate-expand-manager 0.10')
    netlogo.command('set rate-shrink 0.05')
    netlogo.command('set rate-shrink-manager 0.05')
    netlogo.command('set rate-shrink-quit 0.30')
    netlogo.command('set p-quit-tourism 0.05')
    netlogo.command('set p-consider-tourism 0.2')
    netlogo.command('set p-consider-manager 0.2')
    netlogo.command('set n-runs 10')
    netlogo.command('setup')


def run_simulation(driver):
    tf = 'TRUE' if driver[0] else 'FALSE'
    netlogo.command('set succession-issue? ' + tf)
    tf = 'TRUE' if driver[1] else 'FALSE'
    netlogo.command('set leisure-farm? ' + tf)
    tf = 'TRUE' if driver[2] else 'FALSE'
    netlogo.command('set diversification? ' + tf)
    tf = 'TRUE' if driver[3] else 'FALSE'
    netlogo.command('set industrialization? ' + tf)
    netlogo.command('get_ensembles')


with mp.Pool(mp.cpu_count(), initializer=initialiser) as executor:
    executor.map(run_simulation, drivers)
