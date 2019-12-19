SDarnRead --> DmapRead
SDarnRead --> SDConversionUtils
SDarnReed --> SDChecks

SDarnWrite --> SDConversionUtils
SDarnWrite --> DMapWrite 
SDarnWrite --> SDChecks 

SDarnRead : records_dict
SDarnRead : records_dmap_struct
SDarnRead : array_dict (future)
SDarnRead : read_iqdat()
SDarnRead : read_rawacf()
SDarnRead : read_fitacf()
SDarnRead : read_grid()
SDarnRead : read_map()

SDConversionUtils : dict2dmap() 
SDConversionUtils : dmap2dict()
SDConversionUtils : dict2array()
SDConversionUtils : array2dict()

SDChecks : extra_fields_check()
SDChecks : missing_fields_check()
SDChecks : data_types_check()

DmapRead : records
DmapRead : integrity_check()
DmapRead : read_records()

