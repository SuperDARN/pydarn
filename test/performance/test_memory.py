import pydarn
import profile


@profile
def dmap_mem_profile():
    fitacf_file = "../testfiles/20180220.0001.00.rkn.3.0.fitacf"
    dmap = pydarn.DmapRead(fitacf_file)
    dmap_data = dmap.read_records()
    return dmap_data


@profile
def iqdat_mem_profile():
    iqdat_file = "../testfiles/20160316.1945.01.rkn.iqdat"
    darn = pydarn.DarnRead(iqdat_file)
    iqdat_data = darn.read_iqdat()
    return iqdat_data


@profile
def rawacf_mem_profile():
    rawacf_file = "../testfiles/20170410.1801.00.sas.rawacf"
    darn = pydarn.DarnRead(rawacf_file)
    rawacf_data = darn.read_rawacf()
    return rawacf_data


@profile
def fitacf_mem_profile():
    fitacf_file = "../testfiles/20180220.0001.00.rkn.3.0.fitacf"
    darn = pydarn.DarnRead(fitacf_file)
    fitacf_data = darn.read_fitacf()
    return fitacf_data


@profile
def grid_mem_profile():
    grid_file = "../testfiles/20180220.C0.rkn.grid"
    darn = pydarn.DarnRead(grid_file)
    grid_data = darn.read_grid()
    return grid_data


@profile
def map_mem_profile():
    map_file = "../testfiles/20170114.map"
    darn = pydarn.DarnRead(map_file)
    map_data = darn.read_map()
    return map_data


if __name__ == '__main__':
    print('='*80)
    print('WARNING: Values may be skewed from pythons garbage collection')
    print('If you want more accurate profiling please run only of the'
          ' test functions')
    print('='*80)
    data = dmap_mem_profile()
    del data

    data = iqdat_mem_profile()
    del data

    data = rawacf_mem_profile()
    del data
    data = fitacf_mem_profile()
    del data
    data = grid_mem_profile()
    del data
    data = map_mem_profile()
    del data
