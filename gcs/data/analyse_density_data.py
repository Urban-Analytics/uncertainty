import sys, os
import numpy as np
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import matplotlib.pyplot as plt
from geovoronoi.plotting import subplot_for_map, plot_voronoi_polys_with_points_in_area
import pickle

import read_traj


# import from parent directory
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import voronoi as pv

# xmin, xmax, ymin, ymax
zone1 = (8, 20, 8, 22)
zone2 = (38, 50, 8, 22)
zone0 = (0, 52, 0, 50)

IMAGE_DIMENSIONS = (53, 50)
FPS = 25

# Measure density in each (division x division) square of the environment

# this can be overwritten to get locations of pedestrians from a simulation instead of from data
def get_ped_locations(frame_no):
    # Divide by 10 as data is in centimetres instead of metres
    return np.array(read_traj.pedestrian_locations(frame_no)) / 10


# division was 10 but I think that's from when the image was (530, 500)
# so I've changed division to 1
def plot_density(frame_no, division=2):
    points = get_ped_locations(frame_no)
    fig, ax = subplot_for_map()
    x_min = 0
    y_min = 0
    x_max = IMAGE_DIMENSIONS[0]
    y_max = IMAGE_DIMENSIONS[1]
    density_map = np.zeros((int((y_max-y_min) / division),
                            int((x_max-x_min) / division)))
    env_shape = pv.get_region_poly((x_min, x_max, y_min, y_max))
    voronoi_polys, voronoi_points = pv.voronoi_regions_from_coords(points, env_shape)
    # NOTE: colours are random
    plot_voronoi_polys_with_points_in_area(ax, env_shape, voronoi_polys, points, voronoi_points)
    zone1_poly = pv.get_region_poly(zone1)
    zone2_poly = pv.get_region_poly(zone2)
    plt.plot(*zone1_poly.exterior.xy)
    plt.plot(*zone2_poly.exterior.xy)
    plt.show()




### This method is definitely correct. Validated against jupedsim results."""
def zone_density(zone_coords, train=True):
    """ Calculate the voronoi density of the zone, averaged over time. """
    env = (0, IMAGE_DIMENSIONS[0], 0, IMAGE_DIMENSIONS[1])
    density_sum = 0
    total_samples = 0
    i = 0
    if train:
        # get first 20 minutes
        densities = np.empty(40)
        S = range(1, 1200, 30)
    else:
        # last 13.5 minutes
        densities = np.empty(27)
        S = range(1200, 2000, 30)
    for second in S:
        #print('second', second)
        total_samples += 1
        frame_no = second * FPS
        # Note that read_traj scales the data to the image dimensions
        points = get_ped_locations(frame_no)
        density = pv.get_voronoi_density(env, zone_coords, points)
        densities[i] = density
        density_sum += density
        print(density)
        i += 1
    with open('test.pkl', 'wb') as pfile:
        pickle.dump(densities, pfile)
    print(density_sum / total_samples)
    return densities, density_sum / total_samples


def zone_densities(zones):
    total_zones = len(zones)
    zone_results = np.zeros(total_zones)
    env = (0, IMAGE_DIMENSIONS[0], 0, IMAGE_DIMENSIONS[1])
    density_sum = 0
    total_samples = 0
    i = 0
    for second in range(1, 1200, 30):
        print('second', second)
        total_samples += 1
        frame_no = second * FPS
        # Note that read_traj scales the data to the image dimensions
        points = get_ped_locations(frame_no)
        for zn in range(total_zones):
            density = pv.get_voronoi_density(env, zones[zn], points)
            zone_results[zn] += density
        i += 1
    return zone_results / total_samples


def save(average_density, filename='average_density.pkl'):
    with open(filename, 'wb') as pfile:
        pickle.dump(average_density, pfile)

def load(filename='average_density.pkl'):
    with open(filename, 'rb') as pfile:
        average_density = pickle.load(pfile)
    return average_density


GATE_LOCS = (((-1, -1), (10, 30)),
             ((0, 18), (51, 51)),
             ((32, 50), (51, 51)),
             ((53, 53), (43, 50)),
             ((53, 53), (30, 39)),
             ((53, 53), (14, 25)),
             ((53, 53), (0, 8)),
             ((39, 52), (-1, -1)),
             ((26, 39), (-1, -1)),
             ((13, 26), (-1, -1)),
             ((0, 13), (-1, -1)))
H, V = 0, 1
GATE_ORIENTATIONS = (V, H, H, V, V, V, V, H, H, H, H)


def plot(average_density):
    division = 1  # maybe
    plt.imshow(plt.imread('figures/concourse.png'),
               extent=(1, IMAGE_DIMENSIONS[0]/division,
                       1, IMAGE_DIMENSIONS[1]/division), alpha=1)
    print(len(average_density))
    print(len(average_density[0]))
    im = plt.imshow(average_density, cmap='jet', origin='lower',
               interpolation="nearest", alpha=0.8, extent=(0, 52, 0, 50), aspect=1)
    plt.colorbar(im, ticks=(0, 0.2, 0.4, 0.6, 0.79), label='Density')
    plt.xticks((0, IMAGE_DIMENSIONS[0]-1))
    plt.yticks((0, IMAGE_DIMENSIONS[1]))
    for zone in (zone1, zone2, zone0): #, zone4, zone5, zone6, zone7):
        zone_poly = pv.get_region_poly(zone)
        plt.plot(*zone_poly.exterior.xy, c='yellow')
    plt.text(x=zone0[0]+19, y=zone0[2]+2, s='Zone 0', fontsize=16, c='white')
    plt.text(x=zone1[0], y=zone1[2]-3, s='Zone 1', fontsize=16, c='white')
    plt.text(x=zone2[0], y=zone2[2]-3, s='zone 2', fontsize=16, c='white')
    for gate_no in range(11):
        loc = GATE_LOCS[gate_no]
        plt.plot(loc[0], loc[1], marker='o', color='black')
        if GATE_ORIENTATIONS[gate_no] == H:
            if loc[1][0] == -1: y = -5
            else: y = 52
            x = np.mean(loc[0][0]) + 2
            r = 0
        else:
            if loc[0][0] == -1: x = -5
            else: x = 54
            y = np.mean(loc[1][0] + 2)
            r = 90
        plt.text(x, y, s='Gate %d' % gate_no, rotation=r)
    plt.axis('off')
    plt.xlim(-2, 56)
    plt.ylim(-2, 52)
    plt.gca().set_aspect('equal')
    plt.show()



if __name__ == '__main__':
    plot(load())
    
