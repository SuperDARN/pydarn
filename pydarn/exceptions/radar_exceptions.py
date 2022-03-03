# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author(s): Marina Schmidt
import logging
import pydarn
import os

pydarn_log = logging.getLogger('pydarn')


class HardwareFileNotFoundError(Exception):
    """
    This error is raised when a hardware file for the provided
    abbreviation is not found.
    """
    def __init__(self, abbrev):
        self.abbreviation = abbrev
        self.path = os.path.dirname(pydarn.__file__)
        self.message = "Hardware file for {abv} radar was not found"\
            " in {path}/utils/hdw/."\
            " Please ensure the abbreviation is correct and there"\
            " exists a hardware file for it by checking:"\
            " https://github.com/superdarn/hdw. If this error occurs when"\
            " installing pydarn, please make an issue on the github page:"\
            "https://github.com/SuperDARN/pydarn/issues/new so that"\
            " developers are aware and can fix the problem."\
            " Please note hardware files are not obtained by RST."\
            "".format(abv=self.abbreviation, path=self.path)
        super().__init__(self.message)
        pydarn_log.error(self.message)


class RangeEstimationError(Exception):
    """
    This error is raised when there is an incorrect range estimation
    used.
    """
    def __init__(self, msg):
        self.message = msg
        super().__init__(self.message)
        pydarn_log.error(self.message)

