import sys, os
import csv
import numpy as np
#from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
from collections import defaultdict
import scipy.io

# import from parent directory
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
import voronoi as pv


X_MAX = 720
Y_MAX = 480
FPS = 25  # frames per second
DATA_DIMENSIONS = (720, 480)
#IMAGE_DIMENSIONS = (223, 214)  # actual image
IMAGE_DIMENSIONS = (530, 500)  #TODO: need to change it to this
SCALE = (IMAGE_DIMENSIONS[0] / DATA_DIMENSIONS[0],
         IMAGE_DIMENSIONS[1] / DATA_DIMENSIONS[1])


#Each line has: [''x', 'y', 'time']
tracks = scipy.io.loadmat('trajectoriesNew/trajectoriesNew.mat')['trks'][0]


def plot_video(time_start, time_end):
    """ Plot scatter graph of pedestrian movement over the given time frame. """
    # get frame info
    time_start = time_start * FPS
    time_end = time_end * FPS
    frames = defaultdict(list)
    #NOTE: not reading all tracks as it takes too long, this is a bit of a hack
    for agent in range(len(tracks[:1000])):
        X, Y, T = tracks[agent]
        X, Y, T = X.flatten(), Y.flatten(), T.flatten()
        # if the person starts or ends their movement within the time frame
        if (time_start <= T[0] < time_end) or (time_start <= T[-1] < time_end):
            Y = -1.*Y + 455. # because for some reason the data is upside down
            for j in range(len(X)):
                # not all of their moves may in the time frame
                if time_start <= T[j] < time_end:
                    frames[T[j]].append((int(agent), int(X[j]), int(Y[j])))
    # plot the frames
    plt.ion()
    fig, ax = plt.subplots()
    img = plt.imshow(plt.imread('concourse.png'),
                     extent=(0, IMAGE_DIMENSIONS[0], 0, IMAGE_DIMENSIONS[1]))
    plt.xlim(0, IMAGE_DIMENSIONS[0])
    plt.ylim(0, IMAGE_DIMENSIONS[1])
    plt.gca().set_aspect('equal', adjustable='box')
    plt.draw()
    sc = ax.scatter([], [])
    for frame in range(time_start, time_end):
        new = []
        for agentid, x, y in frames[frame]:
            x = x * SCALE[0]
            y = y * SCALE[1]
            new.append((x, y))
        sc.set_offsets(new)
        fig.canvas.draw_idle()
        # Pause for 0.04 seconds to match the video framerate of 250 fps.
        plt.pause(0.04)


def pedestrian_locations(t):
    """ Get locations at frame t."""
    points = []
    for agent in range(len(tracks)):
        X, Y, T = tracks[agent]
        X, Y, T = X.flatten(), Y.flatten(), T.flatten()
        Y = -1.*Y + 455. # because for some reason the data is upside down
        X = X * SCALE[0]
        Y = Y * SCALE[1]
        for j in range(len(X)):
            if T[j] == t:
                points.append((X[j], Y[j]))
    return points

def plot_voronoi(t):
    """ Plot the Voronoi diagram at frame t. """
    # Get pedestrian locations
    points = pedestrian_locations(t)
    pv.plot_voronoi(np.array(points), IMAGE_DIMENSIONS[0], IMAGE_DIMENSIONS[1])


if __name__ == '__main__':
    #plot_voronoi(1*60*FPS)
    plot_video(0, 20)
