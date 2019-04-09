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
        self.message = "Error: Incorrect RTP method is being called for {parameter} of type {data_type}. plot_range_time is for array data types, and plot_time_series is for scalar data types.".format(parameter=self.parameter, data_type=self.data_type)


