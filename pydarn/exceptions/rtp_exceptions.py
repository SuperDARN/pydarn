# Copyright (C) SuperDARN Canada, Universtiy of Saskatchewan
# Authors: Marina Schmidt
import logging

pydarn_log = logging.getLogger('pydarn')


class RTPZeroError(Exception):
    """
    Error raised when a ZeroDivisionError is raised due to minimum - maximum
    range cause mathematical errors in the plotting. An example of this is
    when pwr0 is plotted, some files will have a pwr0=0 which will cause
    a ZeroDivisionError using logNorm as the normalization method. This
    cannot be avoided and challenging to detect which normalization method
    is passed in. Thus error will be raised to let the user know to change
    the range or normalization method to fix the problem.
    """
    def __init__(self, parameter: str, beam_num: int, zmin: float, zmax: float,
                 norm):
        self.parameter = parameter
        self.beam_num = beam_num
        self.zmin = zmin
        self.zmax = zmax
        self.norm = norm
        self.message = "ZeroDivisionError or ValueError is raised "\
            "due to trying to normalize {zmin} to {zmax} using the {norm} "\
            "method for the parameter {param} at beam {num}. "\
            "This can be an issue with the data file, fields meaning"\
            " something different. To resolve this error, please set the "\
            "zmin or zmax parameter or try another normalization"\
            " method.".format(zmin=zmin, zmax=zmax, norm=norm,
                              num=beam_num, param=parameter)
        super().__init__(self.message)
        pydarn_log.error(self.message)
