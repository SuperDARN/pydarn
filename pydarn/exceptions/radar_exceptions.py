# Copyright (C) 2020 SuperDARN Canada, University of Saskatchewan
# Author(s): Marina Schmidt
import logging

pydarn_log = logging.getLogger('pydarn')


class HardwareFileNotFoundError(Exception):
    """
    This error is raised when a hardware file for the provided
    abbreviation is not found.
    """
    def __init__(self, abbrev):
        self.abbreviation = abbrev
        self.message = "Hardware file for {} radar was not found."\
            " Please insure the abbreviation is correct and there"\
            " exists a hardware file for it by checking:"\
            " https://github.com/vtsuperdarn/hdw.dat"\
            "".format(self.abbreviation)

        super().__init__(self.message)
        pydarn_log.error(self.message)
