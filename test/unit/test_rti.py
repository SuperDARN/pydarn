import pydarn
import matplotlib.pyplot as plt

fitacf_file = "../testfiles/20181209.C0.sas.fitacf"
darn_read = pydarn.DarnRead(fitacf_file)
fitacf_data = darn_read.read_fitacf()

pydarn.RTI.plot_profile(fitacf_data, parameter='elevation', beamnum=7, ground_scatter=False)
plt.title("Elevation")
plt.show()
