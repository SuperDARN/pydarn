# Author: Marci Detwiller
import logging
pydarn_logger = logging.getLogger('pydarn')


class BorealisConversionTypesError(Exception):
    """
    SuperDARN Borealis filetype cannot be converted to desired type.

    Parameter
    --------
    filename : str
        name of the file attempting to convert
    dmap_filetype : str
        desired SuperDARN legacy dmap type 
    """
    def __init__(self, filename: str, origin_filetype: str, dmap_filetype: str):
        self.filename = filename
        self.origin_filetype = origin_filetype
        self.dmap_filetype = dmap_filetype
        self.message = "Error: {filename} cannot be converted from its origin_filetype "
                       "{origin_filetype} to legacy dmap filetype {dmap_filetype} because the "
                       "types are not compatible.".format(filename=self.filename,
                        origin_filetype=self.origin_filetype, dmap_filetype=self.dmap_filetype)