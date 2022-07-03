#%%
import pydarn
import pydarnio

import matplotlib.pyplot as plt
from datetime import datetime
from pydarn import Coords


#Read in fitACF file using SuperDARDRead, then read_fitacf
# sps_fitacf_file = 'home/fran/code/SuperdarnW3usr/ForGitRepo/data_vt_mcm/'
mcm_fitacf_file = '/home/fran/code/SuperdarnW3usr/20170101.0000.01.mcm.a.fitacf'

# sps_fitacf_reader = pydarnio.SDarnRead(sps_fitacf_file)
# sps_fitacf_data = sps_fitacf_reader.read_fitacf()

mcm_fitacf_reader = pydarnio.SDarnRead(mcm_fitacf_file)
mcm_fitacf_data = mcm_fitacf_reader.read_fitacf()


"""fig = plt.figure(figsize=(12,12))
kwargs1 = {
    'boundary': True,
    'groundscatter': True,
    'scan_index':22,
    'line_color':'red',
    'radar_label': True,
}

pydarn.Fan.plot_fan(sps_fitacf_data,colorbar=True, **kwargs1)
pydarn.Fan.plot_fan(mcm_fitacf_data,colorbar=False, **kwargs1)"""



# pydarn.Fan.plot_fan(sps_fitacf_data,colorbar=True, **kwargsl2)
# pydarn.Fan.plot_fan(mcm_fitacf_data,colorbar=False, **kwargsl2)

fig1 = plt.figure(figsize=(12,12))
kwargs2 = {
    'boundary': True,
    'zmax': 200,
    'zmin': -200,
    'groundscatter': False,
    'scan_index':22,
    'colorbar_label':'Power [dB]',
    'cmap':'viridis',
    'line_color':'red',
    'radar_label': True,
    'parameter': 'p_l',
    'coords': Coords.SLANT_RANGE
}

# pydarn.Fan.plot_fan(sps_fitacf_data,colorbar=True, **kwargs2)
pydarn.Fan.plot_fan(mcm_fitacf_data,colorbar=False)


plt.show()
# %%
