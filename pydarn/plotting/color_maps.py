import matplotlib.colors as mcol


class PyDARNColormaps():
    PYDARN_VELOCITY =\
            mcol.LinearSegmentedColormap.from_list("pydarn_velocity",
                                                   ["darkred", "r",
                                                    'pink', "b", "darkblue"])

    PYDARN_VIRIDIS =\
        mcol.LinearSegmentedColormap.from_list("pydarn_viridis",
                                               ["indigo", "midnightblue",
                                                "navy", "mediumblue",
                                                "teal",
                                                "mediumseagreen",
                                                "limegreen", "yellowgreen",
                                                "yellow", "gold"])

    PYDARN =\
        mcol.LinearSegmentedColormap.from_list("pydarn", ["midnightblue",
                                                          "darkblue",
                                                          "mediumblue",
                                                          "rebeccapurple",
                                                          "purple",
                                                          "darkmagenta",
                                                          "mediumvioletred",
                                                          "crimson", "red",
                                                          "orangered",
                                                          "darkorange",
                                                          "orange", "gold"])
