import numpy as np
from shapely.geometry import Polygon

from geovoronoi import voronoi_regions_from_coords


def get_region_poly(shape):
    x_min, x_max, y_min, y_max = shape
    return Polygon(((x_min, y_min), (x_min, y_max),
                    (x_max, y_max), (x_max, y_min)))


def get_voronoi_density(environment, region, XY_points):
    """ Calculate the voronoi density of the region within the environment.

    environment: entire environment containing all XY_points
    region: region of interested measured for density
    environment and region must be a tuple giving (x_min, x_max, y_min, y_max).
    XY_points: all XY points within the environment
    """
    # convert to polysgons
    environment_poly = get_region_poly(environment)
    region_poly = get_region_poly(region)
    voronoi_polys, voronoi_points = voronoi_regions_from_coords(XY_points, environment_poly)
    region_density = 0
    for _, vpoly in voronoi_polys.items():
        if vpoly.intersects(region_poly):
            intersection = vpoly.intersection(region_poly)
            region_density += intersection.area / vpoly.area
    return region_density / region_poly.area


if __name__ == "__main__":
    points = ((11.71, 9.95), (37.43, 11), (31.61, 9.77), (22.54, 45.6),
                (44.52, 9.4), (47.97, 22.37), (51.53, 21.18), (43.82, 49.72),
                (39.26, 26.18), (25.14, 6.26), (36, 15.18), (27.96, 33.21),
                (14.65, 48.59), (13.94, 7.78), (15.61, 18.99), (34.92, 8.94),
                (48.59, 24.8), (38.82, 18.81), (37.06, 35.99), (15.3, 39.26),
                (22.73, 31.19), (45.88, 15.55), (14.26, 28.55), (17.83, 20.37),
                (32.74, 26.07), (14.17, 21.44), (50.5, 16.2), (43.64, 15.53),
                (11.88, 21.08), (50.55, 23.29), (40.16, 11.82), (18.48, 17.84),
                (35.18, 31.96), (40.68, 22.51), (47.82, 12.59), (14.24, 24.64),
                (26.71, 30.92), (29.47, 10.45), (31.92, 7.89), (44.7, 13.28),
                (17.18, 40.74), (13.45, 32.37), (30.41, 33.64), (16.44, 16.8),
                (29.19, 7.91), (52.59, 35.16), (3.96, 29.61), (19.05, 34.8),
                (43.18, 37.49), (33.21, 13.25), (37.47, 8.68), (34.51, 6.18),
                (10.36, 25.3), (11.89, 44.14), (35.23, 12.16), (17.4, 12.73),
                (43.47, 6.58), (47.36, 42.59), (22.35, 4.67), (4.44, 45.53))
    points = ((38.31, 5.75), (39.56, 43.81), (49, 21.93), (26.7, 0.07), (18.03, 45.7), (32.44, 9.51), (48.89, 24.23), (39.98, 1.09), (33.95, 47.37), (41.25, 25.36), (46.38, 23.36), (46.21, 43.94), (10.58, 46.55), (8.59, 49.16), (16.43, 6.34), (30.54, 38.12), (38.58, 15.95), (34.26, 11.34), (15.98, 37), (47.48, 25.58), (17.01, 31.16), (16.19, 34.64), (37.59, 22.45), (35.89, 21.83), (39.83, 23.59), (50.51, 24.8), (27.22, 30.63), (27.71, 34.31), (13.45, 14.58), (26.96, 28.01), (41.54, 29.33), (15.57, 30.06), (34.52, 14.02), (51.29, 22.35), (5.55, 41.64), (22.59, 27.45), (24.85, 28.05), (17.05, 17.88), (40.7, 15.22), (47.67, 39.04), (49.32, 41.9), (16.05, 23.32), (13.43, 30.84), (17.81, 19.6), (14.44, 6.09), (25.01, 38.27), (23.06, 33.55), (45.72, 49.24), (37.01, 14.93), (15.27, 16.81), (32.57, 12.62), (6.81, 17.47), (44.99, 37.3), (3.58, 25.98), (13.48, 46.32), (7.89, 42.24), (42.06, 41.65), (29.71, 9.95), (17.79, 11.31), (5.21, 43.98), (35.44, 41.74))
    environment = (0, 53, 0, 50)
    #region = (38, 50, 8, 22)  # measured region, xmin, xmax, ymin, ymax
    region = (8, 20, 8, 22)
    #XY_points = np.array(((40, 11), (45, 20), (1, 6), (8, 9)))  # must be np array
    XY_points = np.array(points)

    print(get_voronoi_density(environment, region, XY_points))
