import pydarn
import dmap  # pip install darn-dmap
import matplotlib.pyplot as plt

map_file = "/Users/chartat1/Downloads/20180501.n.map"
map_data = dmap.read_map(map_file)
pydarn.Maps.plot_mapdata(
    map_data,
    record=15,
    parameter=pydarn.MapParams.RAW_VELOCITY,
    lowlat=50,
    contour_fill=True,
    contour_colorbar=True,
)
plt.show()
