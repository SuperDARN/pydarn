import pydarn
import cProfile, pstats, io
import logging
import os

logging.getLogger('pydarn').setLevel(logging.INFO)
#@profile
#def mem_profile():
dmap = pydarn.DmapRead("../testfiles/20170410.1801.00.sas.rawacf")
pr = cProfile.Profile()
pr.enable()
d = dmap.read_records()
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print("Performance for Dmap Read")
print(s.getvalue())

dmap = pydarn.DmapRead("../testfiles/20170410.1801.00.sas.rawacf")
dmap_data = dmap.read_records()
dmap_write = pydarn.DmapWrite(dmap_data)
pr = cProfile.Profile()
pr.enable()
d = dmap.write_dmap("test_dmap_performance.dmap")
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print("Performance for Dmap Read")
print(s.getvalue())

os.remove("test_dmap_performance.dmap")
#mem_profile()
