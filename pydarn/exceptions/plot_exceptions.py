# Copyright (C) SuperDARN Canada, University of Saskatchewan
# Authors: Marina Schmidt
import logging
import datetime

pydarn_log = logging.getLogger('pydarn')


class IncorrectPlotMethodError(Exception):
    """
    This error is raised when the incorrect plotting
    method is called for a given parameter
    """
    def __init__(self, parameter: str, data_type: str):
        self.parameter = parameter
        self.data_type = data_type
        self.message = "Incorrect plotting method is being called for"\
            " {parameter} of type {data_type}. This plot method is for"\
            " array data types, please look at scalar plotting methods "\
            " for this data types.".format(parameter=self.parameter,
                                           data_type=self.data_type)
        super().__init__(self.message)
        pydarn_log.error(self.message)


class IncorrectDateError(Exception):
    """
    This error is raised when the file dates and plotting
    date do not match
    """
    def __init__(self, record_date: datetime.datetime,
                 plot_date: datetime.datetime):
        self.record_date = record_date
        self.plot_date = plot_date
        self.message = "Incorrect date in record {record_date} or "\
            "plotting date {plot_date}"\
            "".format(record_date=self.record_date.strftime('%Y%m%d %H:%M'),
                      plot_date=self.plot_date.strftime('%Y%m%d %H:%M'))
        super().__init__(self.message)
        pydarn_log.error(self.message)


class NoDataFoundError(Exception):
    """
    This error is raised when no data is found for
    the given beam and parameter
    """
    def __init__(self, parameter: str, beam_num: int, start_time: int,
                 end_time: datetime.datetime, opt_beam_num: int):
        self.parameter = parameter
        self.beam_num = beam_num
        if start_time is None or end_time is None:
            self.message = "There is no Data for beam number {beam_num}"\
                " for the parameter type {parameter}. Try another beam, for"\
                " example: {opt_beam} or another parameter for the given"\
                " time range.".format(parameter=self.parameter,
                                      beam_num=self.beam_num,
                                      opt_beam=opt_beam_num)
        else:
            self.start_time = start_time
            self.end_time = end_time
            self.message = "There is no Data for beam number {beam_num}"\
                " for the parameter type {parameter} between the"\
                " time range {start_time} to"\
                " {end_time}. Try another beam, for example: {opt_beam}"\
                " or another parameter for the given time range."\
                "".format(parameter=self.parameter,
                          beam_num=self.beam_num,
                          opt_beam=opt_beam_num,
                          start_time=self.start_time.strftime("%Y %m"
                                                              " %d %H"
                                                              ":%M"),
                          end_time=self.end_time.strftime("%Y %m"
                                                          " %d %H:%M"))
        super().__init__(self.message)
        pydarn_log.error(self.message)


class CartopyMissingError(Exception):
    """
    Error given when attmpting a cartopy style plot but cartopy isn't installed
    """
    def __init__(self):
        self.message = 'An attempt to plot using cartopy was made'\
            ' without cartopy being installed. Please either change'\
            ' plot styles or install cartopy and dependencies.'
        super().__init__(self.message)
        pydarn_log.error(self.message)


class UnknownParameterError(Exception):
    """
    Error raised when the parameter is not found in the data passed in
    """
    def __init__(self, parameter: str):
        self.parameter = parameter
        self.message = "The following parameter {parameter}"\
            " was not found in the"\
            " data set. Please make sure it is typed correctly or"\
            " you are using the correct data.".format(parameter=self.parameter)
        super().__init__(self.message)
        pydarn_log.error(self.message)


class OutOfRangeGateError(Exception):
    """
    This error is raise when range gate requested is out of range.
    """
    def __init__(self, parameter: str, gate_num: int, max_range_gate: int):
        self.parameter = parameter
        self.gate_num = gate_num
        self.max_range_gate = max_range_gate
        self.message = "The range gate {gate_num} is out of range for this"\
            " parameter {param}. Please pick a range gate number"\
            " between 0 - {max_gate}".format(gate_num=self.gate_num,
                                             param=self.parameter,
                                             max_gate=self.max_range_gate-1)
        super().__init__(self.message)
        pydarn_log.error(self.message)
