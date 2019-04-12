import pydarn
import matplotlib.pyplot as plt

fitacf_file = "../testfiles/20181209.C0.sas.fitacf"
darn_read = pydarn.DarnRead(fitacf_file)
fitacf_data = darn_read.read_fitacf()

fig, ax1 = plt.subplots()
fig.subplots_adjust(hspace=0.5)

pydarn.RTP.plot_range_time(fitacf_data, parameter='elevation', beamnum=7, ax=ax1, ground_scatter=False)
ax1.set_title("Elevation")
ax1.set_xlabel("date")
ax1.set_ylabel("Elevation")


#t = range(0, 20)
#s = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
#ax2.plot(t,s)

fig.suptitle("RTI test subplots")

plt.show()
