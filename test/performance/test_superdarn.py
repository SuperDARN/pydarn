import cProfile
import io
import logging
import pstats
import os

import pydarn
"""
Testing script for the performance on the various SuperDARN file types
for read and writing. This script requires files so may fail if the
same structure is not setup.
"""
logging.getLogger('pydarn').setLevel(logging.INFO)
fitacf_file = "../testfiles/20180220.0001.00.rkn.3.0.fitacf"
rawacf_file = "../testfiles/20170410.1801.00.sas.rawacf"
map_file = "../testfiles/20170114.map"
iqdat_file = "../testfiles/20160316.1945.01.rkn.iqdat"
grid_file = "../testfiles/20180220.C0.rkn.grid"
print("*"*60)
print("Performance testing for Darn Read")
print("*"*60)

dmap = pydarn.DarnRead(rawacf_file)
pr = cProfile.Profile()
pr.enable()
d = dmap.read_rawacf()
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print("="*60)
print("Read Rawacf")
print("File: ", rawacf_file)
print("Size: {} MB".format(os.path.getsize(rawacf_file)/1000000))
print("="*60)
print(s.getvalue())

dmap = pydarn.DarnRead(fitacf_file)
pr = cProfile.Profile()
pr.enable()
d = dmap.read_fitacf()
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print("="*60)
print("Read fitacf")
print("File: ", fitacf_file)
print("Size: {} MB".format(os.path.getsize(fitacf_file)/1000000))
print("="*60)
print(s.getvalue())

dmap = pydarn.DarnRead(iqdat_file)
pr = cProfile.Profile()
pr.enable()
d = dmap.read_iqdat()
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print("="*60)
print("Read iqdat")
print("File: ", iqdat_file)
print("Size: {} MB".format(os.path.getsize(iqdat_file)/1000000))
print("="*60)
print(s.getvalue())

dmap = pydarn.DarnRead(map_file)
pr = cProfile.Profile()
pr.enable()
d = dmap.read_map()
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print("="*60)
print("Read map")
print("File: ", map_file)
print("Size: {} MB".format(os.path.getsize(map_file)/1000000))
print("="*60)
print(s.getvalue())

dmap = pydarn.DarnRead(grid_file)
pr = cProfile.Profile()
pr.enable()
d = dmap.read_grid()
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print("="*60)
print("Read grid")
print("File: ", grid_file)
print("Size: {} MB".format(os.path.getsize(grid_file)/1000000))
print("="*60)
print(s.getvalue())


print("*"*60)
print("Performance testing for DarnWrite")
print("*"*60)


dmap = pydarn.DmapRead(rawacf_file)
dmap_data = dmap.read_records()
dmap_write = pydarn.DarnWrite(dmap_data)
pr = cProfile.Profile()
pr.enable()
d = dmap_write.write_rawacf("test_dmap_performance.dmap")
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
os.remove("test_dmap_performance.dmap")
print("="*60)
print("Write Rawacf")
print("File: ", rawacf_file)
print("Size: {} MB".format(os.path.getsize(rawacf_file)/1000000))
print("="*60)
print(s.getvalue())

dmap = pydarn.DmapRead(fitacf_file)
dmap_data = dmap.read_records()
dmap_write = pydarn.DarnWrite(dmap_data)
pr = cProfile.Profile()
pr.enable()
d = dmap_write.write_fitacf("test_dmap_performance.dmap")
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
os.remove("test_dmap_performance.dmap")
print("="*60)
print("Write fitacf")
print("File: ", fitacf_file)
print("Size: {} MB".format(os.path.getsize(fitacf_file)/1000000))
print("="*60)
print(s.getvalue())

dmap = pydarn.DmapRead(iqdat_file)
dmap_data = dmap.read_records()
dmap_write = pydarn.DarnWrite(dmap_data)
pr = cProfile.Profile()
pr.enable()
d = dmap_write.write_iqdat("test_dmap_performance.dmap")
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
os.remove("test_dmap_performance.dmap")
print("="*60)
print("Write iqdat")
print("File: ", iqdat_file)
print("Size: {} MB".format(os.path.getsize(iqdat_file)/1000000))
print("="*60)
print(s.getvalue())

dmap = pydarn.DmapRead(grid_file)
dmap_data = dmap.read_records()
dmap_write = pydarn.DarnWrite(dmap_data)
pr = cProfile.Profile()
pr.enable()
d = dmap_write.write_grid("test_dmap_performance.dmap")
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
os.remove("test_dmap_performance.dmap")
print("="*60)
print("Write grid")
print("File: ", grid_file)
print("Size: {} MB".format(os.path.getsize(grid_file)/1000000))
print("="*60)
print(s.getvalue())

dmap = pydarn.DmapRead(map_file)
dmap_data = dmap.read_records()
dmap_write = pydarn.DarnWrite(dmap_data)
pr = cProfile.Profile()
pr.enable()
d = dmap_write.write_map("test_dmap_performance.dmap")
pr.disable()
s = io.StringIO()
sortby = 'cumtime'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
os.remove("test_dmap_performance.dmap")
print("="*60)
print("Write map")
print("File: ", map_file)
print("Size: {} MB".format(os.path.getsize(map_file)/1000000))
print("="*60)
print(s.getvalue())
