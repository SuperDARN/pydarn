import pydarn
import matplotlib.pyplot as plt

fitacf_file = "../testfiles/20181209.C0.sas.fitacf"
darn_read = pydarn.DarnRead(fitacf_file)
fitacf_data = darn_read.read_fitacf()

print(len(fitacf_data))
for i in range(2000, 2300):
    del fitacf_data[i]
print(len(fitacf_data))

pydarn.RTP.plot_range_time(fitacf_data, parameter='elevation', beamnum=7, ground_scatter=False)
plt.title("Elevation")
plt.show()
