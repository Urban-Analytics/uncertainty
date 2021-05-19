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


IMAGE_DIMENSIONS = (530, 500)
FPS = 25

# Measure density in each (division x division) square of the environment

# this can be overwritten to get locations of pedestrians from a simulation instead of from data
get_ped_locations = lambda frame_no: read_traj.pedestrian_locations(frame_no)


def plot_density(frame_no, division=10):
    points = np.array(get_ped_locations(frame_no))
    fig, ax = subplot_for_map()
    x_min = 0
    y_min = 0
    x_max = int(IMAGE_DIMENSIONS[0] - (IMAGE_DIMENSIONS[0] % division))
    y_max = int(IMAGE_DIMENSIONS[1] - (IMAGE_DIMENSIONS[1] % division))
    density_map = np.zeros((int((y_max-y_min) / division),
                            int((x_max-x_min) / division)))
    env_shape = pv.get_region_poly((x_min, x_max, y_min, y_max))
    voronoi_polys, voronoi_points = pv.voronoi_regions_from_coords(points, env_shape)
    # NOTE: colours are random
    plot_voronoi_polys_with_points_in_area(ax, env_shape, voronoi_polys, points, voronoi_points)
    plt.show()



def zone_density(zone_coords):
    env = (0, IMAGE_DIMENSIONS[0], 0, IMAGE_DIMENSIONS[1])
    average_density = 0
    total_samples = 0
    for second in range(1, 60, 30):
        print('second', second)
        total_samples += 1
        frame_no = second * FPS
        # Note that read_traj scales the data to the image dimensions
        points = np.array(get_ped_locations(frame_no))
        density = pv.get_voronoi_density(env, zone_coords, points)
        average_density += density
    return average_density / total_samples


def plot_density_map(division=20):
    x_min = 0
    y_min = 0
    x_max = int(IMAGE_DIMENSIONS[0] - (IMAGE_DIMENSIONS[0] % division))
    y_max = int(IMAGE_DIMENSIONS[1] - (IMAGE_DIMENSIONS[1] % division))
    density_map = np.zeros((int((y_max-y_min) / division),
                            int((x_max-x_min) / division)))
    env_shape = pv.get_region_poly((x_min, x_max, y_min, y_max))
    total_samples = 0
    for second in range(1, 1200, 30):
        print('second', second)
        total_samples += 1
        frame_no = second * FPS
        # Note that read_traj scales the data to the image dimensions
        points = np.array(get_ped_locations(frame_no))
        voronoi_polys, voronoi_points = pv.voronoi_regions_from_coords(points, env_shape)
        for k in voronoi_points.keys():
            point_i = voronoi_points[k]
            x, y = points[point_i][0] / division
            x = int(x)
            y = int(y)
            region = pv.get_region_poly((x*division,
                                        (x*division)+division,
                                        y*division,
                                        (y*division)+division))
            intersection = voronoi_polys[k].intersection(region)
            density = intersection.area / voronoi_polys[k].area  # should be intersection with divistion area
            density_map[y][x] += density
    density_map /= total_samples
    save(density_map)
    plot(density_map)


def save(average_density, filename='average_density.pkl'):
    with open(filename, 'wb') as pfile:
        pickle.dump(average_density, pfile)

def load(filename='average_density.pkl'):
    with open(filename, 'rb') as pfile:
        average_density = pickle.load(pfile)
    return average_density


def plot(average_density):
    #plt.imshow(plt.imread('concourse.png'),
    #           extent=(0, IMAGE_DIMENSIONS[0]/division,
    #                   0, IMAGE_DIMENSIONS[1]/division))
    plt.imshow(average_density, cmap='jet', origin='lower',
               interpolation="nearest", alpha=0.6)
    zone2 = Polygon(((4, 4), (4, 11), (10, 11), (10, 4)))
    zone1 = Polygon(((19, 4), (19, 11), (25, 11), (25, 4)))
    x, y = zone2.exterior.xy
    plt.plot(x, y, c='yellow')
    plt.text(x[1], y[1]+1, 'zone 2', c='yellow', fontsize=14)

    x, y = zone1.exterior.xy
    plt.plot(x, y, c='yellow')
    plt.text(x[1], y[1]+1, 'zone 1', c='yellow', fontsize=14)
    plt.gca().set_aspect('equal')
    plt.show()


if __name__ == '__main__':
    zone = ((80, 200, 80, 220))  # zone 1
    #zone = ((380, 500), (80, 220))  # zone 2
    #print(zone_density(zone))
    #plot_density_map()
    #plot_density(1)
    average_density = load()
    plot(average_density)
