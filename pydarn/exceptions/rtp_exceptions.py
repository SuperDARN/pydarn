# Authors: Marina Schmidt
import logging
pydarn_logger = logging.getLogger('pydarn')

class RTPIncorrectPlotMethodError(Exception):
    """
    This error is raised when the incorrect plotting
    method is called for a given parameter
    """
    def __init__(self, parameter, data_type):
        self.parameter = parameter
        self.data_type = data_type
        self.message = "Error: Incorrect RTP method is being called for"\
                " {parameter} of type {data_type}. plot_range_time is for"\
                " array data types, and plot_time_series is for scalar"\
                " data types.".format(parameter=self.parameter,
                                      data_type=self.data_type)


class RTPNoDataFoundError(Exception):
    """
    This error is raised when the incorrect plotting
    method is called for a given parameter
    """
    def __init__(self, parameter, beam_num, start_time, end_time):
        self.parameter = parameter
        self.beam_num = beam_num
        self.start_time = start_time
        self.end_time = end_time
        self.message = "Error: There is no Data for beam number {beam_num}"\
                " for the parameter type {parameter} between the"\
                " time range {start_time} to"\
                " {end_time}".format(parameter=self.parameter,
                                     beam_num=self.beam_num,
                                     start_time=self.start_time.strftime("%Y %m %d %H:%M"),
                                     end_time=self.end_time.strftime("%Y %m %d %H:%M"))


