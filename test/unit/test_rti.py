import pydarn
import matplotlib.pyplot as plt

fitacf_file = "../testfiles/20181209.C0.sas.fitacf"
darn_read = pydarn.DarnRead(fitacf_file)
fitacf_data = darn_read.read_fitacf()

plt.subplot(2, 1, 1)
pydarn.RTP.plot_range_time(fitacf_data, parameter='elevation', beamnum=7, ground_scatter=False)
plt.title("Elevation")

plt.subplot(2, 1, 2)
t = range(0, 20)
s = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
plt.plot(t,s)
plt.show()
