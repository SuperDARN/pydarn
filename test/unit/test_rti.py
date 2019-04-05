import pydarn

fitacf_file = "../testfiles/20181209.C0.sas.fitacf"
darn_read = pydarn.DarnRead(fitacf_file)
fitacf_data = darn_read.read_fitacf()

pydarn.RTI.plot_profile(fitacf_data, paramete='elevation', beamnum=7)

