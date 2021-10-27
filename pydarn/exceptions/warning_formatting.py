# copyright (C) SuperDARN Canada, University of Saskatchewan
# Author(s): Marina Schmidt
#
# Modifications:
#
# Disclaimer: pyDARN is licensed under the GPL v 3.0 found in LICENSE
#
import warnings

def citing_warning():
    """
    prints a citation warning for pyDARN users to remind them to cite
    pyDARN in publications.
    """
    warnings.warn("Please make sure to cite pyDARN in publications that"
              " use plots created by pyDARN using DOI:"
              " https://zenodo.org/record/3727269. Citing information"
              " for SuperDARN data is found at"
              " https://pydarn.readthedocs.io/en/master/user/citing/")


def partial_record_warning():
    """
    prints a warning that the data chosen to be plotted is missing some 
    keys that may produce a blank/half a plot
    """
    warnings.warn("Please be aware that the data chosen to be plotted"
                  " contains a partial record. As such the plot may"
                  " be empty or only partially filled.")

def standard_warning_format(message: str, category: str, filename: str,
                            lineno: int, file: str = None,
                            line: int = None) -> str:
    """
    Sets the standard warning message format to be:
        filename: lineno: category: message

    Parameters
    ----------
        message: str
            warning message to be printed to a user
        category: str
            type of the warning message
        filename: str
            name of the associated to the warning message
        lineno : int
            line number where the warning message was raised
        file : str
        line : str

    Returns
    -------
        formatted warning message to be printed to the console
    """
    return "{filename}: {linenum}: {category}:"\
           " {message}\n".format(filename=filename,
                                 linenum=lineno,
                                 category=category.__name__,
                                 message=message)


def only_message_warning_format(message: str, category: str, filename: str,
                                lineno: int, file: str = None,
                                line: int = None) -> str:
    """
    Sets the standard warning message format to be:
        filename: lineno: category: message

    Parameters
    ----------
        message: str
            warning message to be printed to a user
        category: str
            type of the warning message
        filename: str
            name of the associated to the warning message
        lineno : int
            line number where the warning message was raised
        file : str
        line : str

    Returns
    -------
        formatted warning message to be printed to the console
    """
    return "{filename} {linenum} {category}: {message}\n"\
        "".format(filename=filename, linenum=lineno,
                  category=category.__name__, message=message)
