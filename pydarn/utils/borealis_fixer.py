import sys
import os
import copy
import subprocess as sp
import numpy as np
import warnings
import tables
warnings.filterwarnings('ignore', category=tables.NaturalNameWarning)
import deepdish as dd


def main():
    filename = sys.argv[1]
    fixed_data_dir = sys.argv[2]

    recs = dd.io.load(filename)
    sorted_keys = sorted(list(recs.keys()))

    out_file = fixed_data_dir + "/" + os.path.basename(filename)
    tmp_file = fixed_data_dir + "/" + os.path.basename(filename) + ".tmp"


    write_dict = {}
    
    def convert_to_numpy(data):
        """Converts lists stored in dict into numpy array. Recursive.

        Args:
            data (Python dictionary): Dictionary with lists to convert to numpy arrays.
        """
        for k, v in data.items():
            if isinstance(v, dict):
                convert_to_numpy(v)
            elif isinstance(v, list):
                data[k] = np.array(v)
            else:
                continue
        return data

    for group_name in sorted_keys:

        # APPLY CHANGE HERE
        # recs[group_name]['data_dimensions'][0] = 2
        recs[group_name]['main_acfs'] = recs[group_name]['main_acfs'] * -1 
        recs[group_name]['xcfs'] = recs[group_name]['xcfs'] * -1

        write_dict = {}
        write_dict[group_name] = convert_to_numpy(recs[group_name])
        dd.io.save(tmp_file, write_dict, compression=None)

        # use external h5copy utility to move new record into 2hr file.
        cmd = 'h5copy -i {newfile} -o {twohr} -s {dtstr} -d {dtstr}'
        cmd = cmd.format(newfile=tmp_file, twohr=out_file, dtstr=group_name)

        # TODO(keith): improve call to subprocess.
        sp.call(cmd.split())
        os.remove(tmp_file)


if __name__ == "__main__":
    main()