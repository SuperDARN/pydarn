import pydarn
import matplotlib.pyplot as plt
from datetime import datetime

fitacf_file = "../testfiles/20181209.C0.sas.fitacf"
darn_read = pydarn.DarnRead(fitacf_file)
fitacf_data = darn_read.read_fitacf()


pydarn.RTP.plot_range_time(fitacf_data, parameter='elevation', beamnum=7,
                           ground_scatter=False,
                           norm_range=(0,57))
plt.title("Elevation")
plt.show()
