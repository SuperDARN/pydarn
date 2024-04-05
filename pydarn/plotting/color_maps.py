import matplotlib
from matplotlib import colormaps as cm


class PyDARNColormaps():
    PYDARN_INFERNO = cm.get_cmap('inferno')
    PYDARN_PLASMA = cm.get_cmap('plasma')
    PYDARN_PLASMA_R = cm.get_cmap('plasma_r')
    PYDARN_VELOCITY = matplotlib.colors.LinearSegmentedColormap.from_list(
                        "pydarn_velocity", ["darkred", "r", 'pink', "b",
                                            "darkblue"])

    PYDARN_VIRIDIS = matplotlib.colors.LinearSegmentedColormap.from_list(
                        "pydarn_viridis", ["indigo", "midnightblue",
                                           "navy", "mediumblue",
                                           "teal", "mediumseagreen",
                                           "limegreen", "yellowgreen",
                                           "yellow", "gold"])

    PYDARN = matplotlib.colors.LinearSegmentedColormap.from_list("pydarn",
                ["midnightblue", "darkblue", "mediumblue", "rebeccapurple",
                 "purple", "darkmagenta", "mediumvioletred", "crimson", "red",
                 "orangered", "darkorange", "orange", "gold"])

