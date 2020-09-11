# Authors:
#     Sylvain Faure <sylvain.faure@universite-paris-saclay.fr>
#     Bertrand Maury <bertrand.maury@universite-paris-saclay.fr>
#
#      cromosim/examples/micro/social/micro_social.py
#      python micro_social.py --json input.json
#
# License: GPL


import sys, os
import math
import random
from cromosim import *
from cromosim.micro import *
from optparse import OptionParser
import json


def add_new_person(all_people):
    doors = ['door1', 'door2', 'door3', 'door4', 'door5',
             'door6', 'door7', 'door8', 'door9']
    door_locs = [[2.5, 9, 51, 52.5],
                 [26, 32, 51, 52.5],
                 [31.5, 33, 38.5, 44.5],
                 [31.5, 33, 28, 32.5],
                 [31.5, 33, 15, 22.5],
                 [31.5, 33, 3, 9.5],
                 [25.5, 33.5, 2.5, 4],
                 [2.5, 7, 2.5, 4],        
                 [3.0, 4.5, 27.5, 32.5]]
    # pick a random door to appear from
    loc_i = random.randint(0, 8)
    # remove appearance door from possible exit doors
    doors.pop(loc_i)
    # pick an exit destination door
    dest = doors[random.randint(0, 7)]  # 8 doors remain to choose from
    groups = [{'nb': 1,
               'radius_distribution': ['uniform', 0.4, 0.6],
               'velocity_distribution': ['normal', 1.2, 0.1],
               'box': door_locs[loc_i],
               'destination': dest}] 
    #NOTE: you are not using the seed here as it created duplicate people
    # to fix this, there should hopefully be some kind of seed.next() function
    new_people = people_initialization(dom, groups, dt, dmin_people=dmin_people,
                                    dmin_walls=dmin_walls, itermax=10,
                                    projection_method=projection_method, verbose=False)
    s = all_people[peopledom["domain"]]['last_id']
    sid = len(s) - 5
    s = s[:-sid] + str(int(s[-sid:])+1)
    new_people['id'][0] = s
    all_people[peopledom["domain"]]['last_id'] = s
    for ip,pid in enumerate(new_people["id"]):
            all_people[peopledom["domain"]]["paths"][pid] = new_people["xyrv"][ip,:2]
    I, J, Vd = dom.people_desired_velocity(new_people["xyrv"],
            new_people["destinations"])
    for k in ('xyrv', 'Vd', 'U', 'Uold', 'id', 'destinations'):
        for v in new_people[k]:
            info_space = all_people[peopledom["domain"]][k]
            print(info_space.shape)
            try:
                row, col = all_people[peopledom["domain"]][k].shape
                all_people[peopledom["domain"]][k] = np.resize(all_people[peopledom["domain"]][k], (row+1, col))
            except ValueError:
                row = all_people[peopledom["domain"]][k].size
                all_people[peopledom["domain"]][k] = np.resize(all_people[peopledom["domain"]][k], row+1)
            #print(info_space)
            all_people[peopledom["domain"]][k][-1] = v
    if (with_graphes):
            colors = people["xyrv"][:,2]
            plot_people(100*i+20, dom, people, contacts, colors, time=t,
                        plot_people=plot_p, plot_contacts=plot_c,
                        plot_velocities=plot_v, plot_desired_velocities=plot_vd,
                        plot_sensors=plot_s, sensors=all_sensors[dom.name],
                        savefig=False, filename=prefix+dom.name+'_fig_'+ \
                        str(counter).zfill(6)+'.png')
    #print("===> All people = ",all_people[peopledom["domain"]]['paths'])


plt.ion()

"""
    python micro_social.py --json input.json
"""
parser = OptionParser(usage="usage: %prog [options] filename",
    version="%prog 1.0")
parser.add_option('--json',dest="jsonfilename",default="input.json",
    type="string",
                  action="store",help="Input json filename")
opt, remainder = parser.parse_args()
print("===> JSON filename = ",opt.jsonfilename)
with open(opt.jsonfilename) as json_file:
    try:
        input = json.load(json_file)
    except json.JSONDecodeError as msg:
        print(msg)
        print("Failed to load json file ",opt.jsonfilename)
        print("Check its content \
            (https://fr.wikipedia.org/wiki/JavaScript_Object_Notation)")
        sys.exit()


prefix = input["prefix"]
if not os.path.exists(prefix):
    os.makedirs(prefix)
seed = input["seed"]
with_graphes = input["with_graphes"]
json_domains = input["domains"]
#print("===> JSON data used to build the domains : ",json_domains)
json_people_init = input["people_init"]
#print("===> JSON data used to create the groups : ",json_people_init)
json_sensors = input["sensors"]
#print("===> JSON data used to create sensors : ",json_sensors)
Tf = input["Tf"]
dt = input["dt"]
drawper = input["drawper"]
mass = input["mass"]
tau = input["tau"]  # affects how wide of a curve people make avoiding obstacles
F = input["F"]  # Coefficient for the repulsion force between individuals
kappa = input["kappa"]
delta = input["delta"]
Fwall = input["Fwall"]
lambda_ = input["lambda"]
eta = input["eta"]
projection_method = input["projection_method"]
dmax = input["dmax"]
dmin_people = input["dmin_people"]
dmin_walls = input["dmin_walls"]
plot_p = input["plot_people"]
plot_c = input["plot_contacts"]
plot_v = input["plot_velocities"]
plot_vd = input["plot_desired_velocities"]
plot_pa = input["plot_paths"]
plot_s = input["plot_sensors"]
plot_pa = input["plot_paths"]
print("===> Final time, Tf = ",Tf)
print("===> Time step, dt = ",dt)
print("===> To draw the results each drawper iterations, \
    drawper = ",drawper)
print("===> Maximal distance to find neighbors, dmax = ",
    dmax,", example : 2*dt")
print("===> ONLY used during initialization ! Minimal distance between \
       persons, dmin_people = ",dmin_people)
print("===> ONLY used during initialization ! Minimal distance between a \
       person and a wall, dmin_walls = ",dmin_walls)

"""
    Build the Domain objects
"""
domains = {}
for i,jdom in enumerate(json_domains):
    jname = jdom["name"]
    print("===> Build domain number ",i," : ",jname)
    jbg = jdom["background"]
    jpx = jdom["px"]
    jwidth = jdom["width"]
    jheight = jdom["height"]
    jwall_colors = jdom["wall_colors"]
    if (jbg==""):
        dom = Domain(name=jname, pixel_size=jpx, width=jwidth,
                     height=jheight, wall_colors=jwall_colors)
    else:
        dom = Domain(name=jname, background=jbg, pixel_size=jpx,
                     wall_colors=jwall_colors)
    ## To build the domain : background + shapes
    dom.build_domain()
    ## To add all the available destinations
    for j,dd in enumerate(jdom["destinations"]):
        desired_velocity_from_color=[]
        for gg in dd["desired_velocity_from_color"]:
            desired_velocity_from_color.append(
                np.concatenate((gg["color"],gg["desired_velocity"])))
        dest = Destination(name=dd["name"],colors=dd["colors"],
        excluded_colors=dd["excluded_colors"],
        desired_velocity_from_color=desired_velocity_from_color,
        velocity_scale=dd["velocity_scale"],
        next_destination=dd["next_destination"],
        next_domain=dd["next_domain"],
        next_transit_box=dd["next_transit_box"])
        print("===> Destination : ",dest)
        dom.add_destination(dest)
        #if (with_graphes):
        #    dom.plot_desired_velocity(dd["name"],id=100*i+10+j,step=20)

    #print("===> Domain : ",dom)
    #if (with_graphes):
        #dom.plot(id=100*i)
        #dom.plot_wall_dist(id=100*i+1,step=20)

    domains[dom.name] = dom

print("===> All domains = ",domains)

"""
    To create the sensors to measure the pedestrian flows
"""

all_sensors = {}
for domain_name in domains:
    all_sensors[domain_name] = []
for s in json_sensors:
    s["id"] = []
    s["times"] = []
    s["xy"] = []
    s["dir"] = []
    all_sensors[s["domain"]].append(s)
    #print("===> All sensors = ",all_sensors)

"""
    Initialization
"""

## Current time
t = 0.0
counter = 0

## Initialize people
all_people = {}
for i,peopledom in enumerate(json_people_init):
    dom = domains[peopledom["domain"]]
    groups = peopledom["groups"]
    print("===> Group number ",i,", domain = ",peopledom["domain"])
    people = people_initialization(dom, groups, dt,
        dmin_people=dmin_people, dmin_walls=dmin_walls, seed=seed,
        itermax=10, projection_method=projection_method, verbose=True)
    I, J, Vd = dom.people_desired_velocity(people["xyrv"],
        people["destinations"])
    people["Vd"] = Vd
    for ip,pid in enumerate(people["id"]):
        people["paths"][pid] = people["xyrv"][ip,:2]
    contacts = None
    if (with_graphes):
        colors = people["xyrv"][:,2]
        plot_people(100*i+20, dom, people, contacts, colors, time=t,
                    plot_people=plot_p, plot_contacts=plot_c,
                    plot_velocities=plot_v, plot_desired_velocities=plot_vd,
                    plot_sensors=plot_s, sensors=all_sensors[dom.name],
                    savefig=False, filename=prefix+dom.name+'_fig_'+ \
                    str(counter).zfill(6)+'.png')
    all_people[peopledom["domain"]] = people
print("===> All people = ",all_people)
#add_new_person(all_people)
#add_new_person(all_people)
#print("===> All people = ",all_people)

#"""
    #Main loop
#"""

cc = 0
draw = True

while (t<Tf and all_people['room']["Uold"].shape[0] > 0):
    print("\n===> Time = "+str(t))
    ## Compute people desired velocity
    for idom,name in enumerate(domains):
        print("===> Compute desired velocity for domain ",name)
        dom = domains[name]
        people = all_people[name]
        I, J, Vd = dom.people_desired_velocity(people["xyrv"],
            people["destinations"])
        people["Vd"] = Vd
        people["I"] = I
        people["J"] = J

    ## Look at if there are people in the transit boxes
    print("===> Find people who have to be duplicated")
    virtual_people = find_duplicate_people(all_people, domains)
    #print("     virtual_people : ",virtual_people)

    ## Social forces
    for idom,name in enumerate(domains):
        print("===> Compute social forces for domain ",name)
        dom = domains[name]
        people = all_people[name]

        try:
            xyrv = np.concatenate((people["xyrv"],
                virtual_people[name]["xyrv"]))
            Vd = np.concatenate((people["Vd"],
                virtual_people[name]["Vd"]))
            Uold = np.concatenate((people["Uold"],
                virtual_people[name]["Uold"]))
        except:
            xyrv = people["xyrv"]
            Vd = people["Vd"]
            Uold = people["Uold"]

        if (xyrv.shape[0]>0):

            if (np.unique(xyrv, axis=0).shape[0] != xyrv.shape[0]):
                print("===> ERROR : There are two identical lines in the")
                print("             array xyrv used to determine the \
                    contacts between")
                print("             individuals and this is not normal.")
                sys.exit()

            contacts = compute_contacts(dom, xyrv, dmax)
            print("     Number of contacts: ",contacts.shape[0])
            Forces = compute_forces( F, Fwall, xyrv, contacts, Uold, Vd,
                                     lambda_, delta, kappa, eta)
            nn = people["xyrv"].shape[0]
            all_people[name]["U"] = dt*(Vd[:nn,:]-Uold[:nn,:])/tau + \
                          Uold[:nn,:] + \
                          dt*Forces[:nn,:]/mass
            ## only for the plot of virtual people :
            virtual_people[name]["U"] = dt*(Vd[nn:,:]-Uold[nn:,:])/tau + \
                          Uold[nn:,:] + \
                          dt*Forces[nn:,:]/mass


            all_people[name], all_sensors[name] = move_people(t, dt,
                                           all_people[name],
                                           all_sensors[name])

        if (draw and with_graphes):
            ## coloring people according to their radius
            colors =  all_people[name]["xyrv"][:,2]
            ## coloring people according to their destinations
            # colors = np.zeros(all_people[name]["xyrv"].shape[0])
            # for i,dest_name in enumerate(all_people[name]["destinations"]):
            #     ind = np.where(all_people[name]["destinations"]==dest_name)[0]
            #     colors[ind]=i
            plot_people(100*idom+20, dom, all_people[name], contacts,
                        colors, virtual_people=virtual_people[name], time=t,
                        plot_people=plot_p, plot_contacts=plot_c,
                        plot_paths=plot_pa, plot_velocities=plot_v,
                        plot_desired_velocities=plot_vd, plot_sensors=plot_s,
                        sensors=all_sensors[dom.name], savefig=False,
                        filename=prefix+dom.name+'_fig_'
                        + str(counter).zfill(6)+'.png')
            plt.pause(0.01)

    ## Update people destinations
    all_people = people_update_destination(all_people,domains,dom.pixel_size)

    ## Update previous velocities
    for idom,name in enumerate(domains):
        all_people[name]["Uold"] = all_people[name]["U"]

    ## Print the number of persons for each domain
    for idom,name in enumerate(domains):
        print("===> Domain ",name," nb of persons = ",
            all_people[name]["xyrv"].shape[0])
    
    if round(t, 3)  % 5.000 == 0:
        add_new_person(all_people)

    t += dt
    cc += 1
    counter += 1
    if (cc>=drawper):
        draw = True
        cc = 0
    else:
        draw = False


#for idom,domain_name in enumerate(all_sensors):
    #print("===> Plot sensors of domain ",domain_name)
    #plot_sensors(100*idom+40, all_sensors[domain_name], t, savefig=False,
                #filename=prefix+'sensor_'+str(i)+'_'+str(counter)+'.png')
    #plt.pause(0.01)

plt.ioff()
plt.show()
sys.exit()
