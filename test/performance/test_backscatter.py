from backscatter import dmap
import cProfile, pstats, StringIO

#@profile
#def mem_profile():
#    dmap = backscatter.backscatter.dmap.dmap.RawDmapRead("20170410.1801.00.sas.rawacf")
pr = cProfile.Profile()
pr.enable()
d = dmap.parse_dmap_format_from_file("20170410.1801.00.sas.rawacf")
pr.disable()
s = StringIO.StringIO()
sortby = 'cumulative'
ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
ps.print_stats()
print(s.getvalue())

#mem_profile()
