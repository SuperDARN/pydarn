import pydarn
import matplotlib.pyplot as plt

fitacf_file = "./20181209.C0.sas.fitacf"
darn_read = pydarn.DarnRead(fitacf_file)
fitacf_data = darn_read.read_fitacf()

pydarn.RTP.plot_time_series(fitacf_data, parameter='sky noise', beam_num=7)
plt.yscale('log')
plt.show()
