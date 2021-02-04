import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
import matplotlib.colors as mcolors
import matplotlib.cm as cm


cmap = ListedColormap(["honeydew", "palegreen", "limegreen", "forestgreen", "darkgreen"])


def _cmap_discretise(cmap, N):
    """Return a discrete colormap from the continuous colormap cmap.

        cmap: colormap instance, eg. cm.jet. 
        N: number of colors.

    Example
        x = resize(arange(100), (5,100))
        djet = _cmap_discretise(cm.jet, 5)
        imshow(x, cmap=djet)
    """
    if type(cmap) == str:
        cmap = plt.get_cmap(cmap)
    colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    indices = np.linspace(0, 1., N+1)
    cdict = {}
    for ki,key in enumerate(('red','green','blue')):
        cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki])
                       for i in range(N+1) ]
    # Return colormap object.
    return mcolors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)


def _colorbar_index(ncolors, cmap):
    cmap = _cmap_discretise(cmap, ncolors)
    mappable = cm.ScalarMappable(cmap=cmap)
    mappable.set_array([])
    mappable.set_clim(-0.5, ncolors+0.5)
    colorbar = plt.colorbar(mappable)
    colorbar.set_ticks(np.linspace(0, ncolors, ncolors))
    colorbar.set_ticklabels(range(ncolors))


def plot(map_filepath="sugarscape_cg/sugar-map.txt"):
    data = np.genfromtxt(map_filepath)
    im = plt.imshow(data, cmap=cmap, rasterized=True, vmin=0, vmax=4)
    _colorbar_index(ncolors=5, cmap=cmap)
    plt.minorticks_on()
    plt.grid(b=True, which='minor', color='#999999', linestyle='-', alpha=0.2)
    plt.show()
