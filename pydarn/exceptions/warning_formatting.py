# copyright (C) SuperDARN Canada, University of Saskatchewan
# Author(s): Marina Schmidt
#
# Modifications:
#
# Disclaimer: pyDARN is licensed under the GPL v 3.0 found in LICENSE
#


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
