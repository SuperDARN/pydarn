# Copyright 2019 SuperDARN Canada, University of Saskatchewan
# Author: Marci Detwiller
"""
This file contains the BaseFormat class which is used to build
all formats of SuperDARN Borealis HDF5 files.

Classes
-------
BaseFormat

Design Concept for Borealis Format Classes
------------------------------------------
In using formats as static classes without instantiation, the
Borealis formats have been developed with inheritance in mind. This
allows restructuring of the formats to be set up within the
BaseFormat parent class, as well as some other basic class methods,
while allowing the format to specify its unique characteristics
(fields and their types) in specified classmethods and staticmethods
which should be rewritten by the class.

All borealis format classes inherit from BaseFormat to make use
of the BaseFormat internal methods used for restructuring.

See Also
--------
- borealis_formats module, where the current formats are set up.
- The Borealis documentation on formats is at
  https://borealis.readthedocs.io/en/latest/borealis_data.html

Notes
-----
- 'borealis_git_hash' and 'sqn_timestamps' are necessary fields for all
  versions and formats. 'borealis_git_hash' is necessary as its use is
  hardcoded  into the code in order to determine the format version to use.
  'sqn_timestamps' is necessary as all formats use this field to restructure
  from site to arrayand vice versa.
"""

from datetime import datetime
import numpy as np

from collections import OrderedDict

from pydarn import borealis_exceptions


class BaseFormat():
    """
    The base format of all Borealis format classes.

    Class Methods that Vary with Format
    -----------------------------------
    All Borealis formats should inherit from this class. The following class
    methods should be specific to the format and therefore should be
    overwritten by the format. These methods classify the fields in
    a format and how they are used in restructuring.

    All fields possible = single_element_types + array_dtypes
    All fields are then also classified into four types to determine
    how to restructure: shared_fields (all records have the same value),
    unshared_fields (all records have unique value/array),
    array_specific_fields (used mainly where dimensions
    may vary between records so the number to parse needs to be stored),
    and site_specific_fields (used mainly where dimensions of
    flattened arrays need to be stored).

    unshared_fields require dimensions to be generated when structuring
    from the opposite type (array/site), and array specific and site specific
    formats require generator functions when converting from the opposite
    type.

    The following class methods classify the field types and provide
    generation information when restructuring from the opposite structure.

    is_restructureable(): bool
        A boolean setting whether the format is restructureable.
        If the format is restructureable, the shared_fields and
        unshared_fields_dims_array and unshared_fields_dims_site
        are necessary to restructure using the
        _site_to_array and _array_to_site class methods.
    single_element_types(): dict
        Dictionary of data field name to type for the format. This
        dictionary should contain all fields in a record
        that are not numpy arrays.
    array_dtypes(): dict
        Dictionary of data field names where numpy arrays are expected,
        to numpy dtype for the format. This dictionary should contain all
        fields that would be an array per record.
    shared_fields(): list
        List of the fields that are common (shared) across records. This
        means that they can be reduced to a single value/array per file when
        they are array restructured.
    unshared_fields_dims_array(): dict
        Unshared field: dimensions per record in array structure. Unshared
        fields are not common across records. In array structure the first
        dimension will be num_records followed by these dimensions. Dimensions
        are provided as functions that will calculate the dimension given the
        records or site data dictionary. This class method is used to convert
        from site structure to array structure.
    unshared_fields_dims_site(): dict
        Unshared field: dimensions per record in site structure. Unshared
        fields are not common across records. These dimensions can vary per
        record so the functions take the arrays data dictionary and the
        record number. This class method is used to convert from array
        structure to site structure.
    array_specific_fields_generate(): dict
        Any fields that are array specific or require specific function to
        generate. The key is the name of the array specific field and the
        value in the dictionary is the function that takes the
        records (site data dictionary) to generate the value for that field.
        This class method is used when restructuring from site to array style.
    site_specific_fields_generate(): dict
        Any fields that are site specific or require specific function to
        generate. The key is the name of the site specific field and the
        value in the dictionary is the function that takes the arrays
        (array data dictionary) and the record_num to generate the value for
        that field at that record number. This class method is used when
        restructuring from array to site style.

    Static Methods that Vary with Format
    ------------------------------------
    The following static methods should be specific to the format and
    can be overwritten by the format.

    reshape_site_arrays(records): OrderedDict
        A function to reshape a record field if it has been flattened
        for storage in the site file (a common convention). The
        fields for reshaping and their dimensions are specific to the
        format. This is a necessary function for interpreting site data.
    flatten_site_arrays(records): OrderedDict
        A function to flatten record fields if needed for storing in the
        site structure. The fields for flattening are specific to the
        format.

    Class Methods Common Across Formats
    -----------------------------------
    These following methods use the format-specific methods above to generate
    their values and therefore should not be overwritten by the format class:

    unshared_fields: list
        List of the fields that are not common across records and therefore
        must be stored as an array with first dimension = num_records in the
        array structure.
    array_specific_fields: list
        List of fields that are only present in array files.
    site_specific_fields: list
        List of fields that are only present in site files.
    site_fields: list
        List of all fields that are in the site file type.
    array_fields: list
        List of all fields that are in the array file type.
    site_single_element_fields : list
        List of fields in the site files that are single element types.
    site_single_element_types: dict
        subset of single_element_types with only site keys.
    site_array_dtypes_fields : list
        List of fields in the site files that are made of numpy arrays.
    site_array_dtypes: dict
        subset of array_dtypes with only site keys.
    array_single_element_fields : list
        List of fields in the array files that are single element types.
        Note that if the field is unshared it will appear as an
        array of the type in the arrays data dictionary so no unshared fields
        will appear in this list.
    array_single_element_types: dict
        subset of single_element_types with only array fields.
    array_array_dtypes_fields : list
        List of fields in the array files that are made of numpy arrays.
        Includes fields that are single element but are unshared so are
        converted to arrays in the array file.
    array_array_dtypes: dict
        fields in the array files that are made of numpy arrays, with their
        given data type.
    _site_to_array(data_dict): dict
        Convert an OrderedDict of site data to array data using the information
        provided for the specific data format.
    _array_to_site(data_dict): OrderedDict
        Convert a dictionary of array data to site data using the information
        provided for the specific data format.

    Static Methods Common Across Formats
    ------------------------------------
    find_max_sequences(records): int
        Find the max number of sequences between records in a site file, for
        restructuring to arrays.
    find_max_beams(records): int
        Find the max number of beams between records in a site file, for
        restructuring to arrays.
    find_max_blanked_samples(records): int
        Find the max number of blanked samples between records in a site file,
        for restructuring to arrays.

    Notes
    -----
    single_element_types.keys() + array_dtypes.keys() = all known fields
    shared_fields + unshared_fields + array_specific_fields = all fields in
        array file
    shared_fields + unshared_fields + site_specific_fields = all fields in
        site file
    """

    # CLASS METHODS THAT VARY BY FORMAT
    # i.e. class methods that classify fields in the format.

    @classmethod
    def is_restructureable(cls):
        """
        Return whether the format is restructureable.

        Returns
        -------
        is_restructureable
            boolean; True if restructureable using _site_to_array
            and _array_to_site defined here in the BaseFormat.

        See Also
        --------
        _site_to_array
        _array_to_site

        Notes
        -----
        Default is False; this should only be set to True if the format has
        shared_fields and unshared_fields properly set up. While most
        distributed formats have been designed to be restructureable, some
        formats, such as BorealisRawrf, have not been. BorealisRawrf
        is a less common format for high bandwidth samples.
        """
        return False

    @classmethod
    def single_element_types(cls):
        """
        Retrieve the fields of the format that are stored as single elements
        in the records.

        Returns
        -------
        single_element_types
            All the single-element fields in records of the
            format, as a dictionary fieldname : type.

        Notes
        -----
        borealis_git_hash is a necessary field for all formats because it
        is used to determine the format to use.
        """
        return {
            # Identifies the version of Borealis that made this data.
            # Necessary for all versions and formats.
            "borealis_git_hash": np.unicode_,
            }

    @classmethod
    def array_dtypes(cls):
        """
        Retrieve the fields of the format that are stored as arrays
        in the records.

        Returns
        -------
        array_dtypes
            All the array fields in records of the
            format, as a dictionary fieldname : array dtype.

        Notes
        -----
        sqn_timestamps is a necessary field for all formats because it
        is used in restructuring and defines the time for any data.
        """
        return {
            # A list of GPS timestamps of the beginning of transmission for
            # each sampling period in the integration time. Seconds since
            # epoch. Necessary for all formats.
            "sqn_timestamps": np.float64,
            }

    @classmethod
    def shared_fields(cls):
        """
        Retrieve the fields of the format that belong in both site
        and array structured files as the same value (the value is
        shared across records).

        Returns
        -------
        List of the fields that are common (shared) across records. This
        means that they can be reduced to a single value/array per file when
        they are array restructured. This is unique to the format so should
        be overwritten by the child class.

        Notes
        -----
        All fields possible = single_element_types + array_dtypes
        Fields are then classified into four types to determine
        how to restructure: shared_fields (all records have the same value),
        unshared_fields (all records have unique value/array),
        array_specific_fields (any fields unique to array files, used mainly
        where dimensions may vary between records so the number to parse needs
        to be stored), and site_specific_fields (any fields unique to site
        files, used mainly where dimensions of flattened arrays need to be
        stored).
        """
        return []

    @classmethod
    def unshared_fields_dims_array(cls):
        """
        Retrieve the fields of the format that belong in both site
        and array structured files as values that vary with record number.
        For every field, a function is given that calculates the
        dimensions for the array structured format.

        Returns
        -------
        A dictionary of the unshared field: dimensions per record
        in array structure. Unshared fields are not common across records.
        In array structure the first dimension will be num_records followed
        by these dimensions. Dimensions are provided as functions that will
        calculate the dimension given the records (site data) dictionary. This
        class method is used to convert from site structure to array structure.
        The unshared fields and the functions to generate their dimensions
        are unique to the format so should be overwritten by the child class.

        Notes
        -----
        All fields possible = single_element_types + array_dtypes
        Fields are then classified into four types to determine
        how to restructure: shared_fields (all records have the same value),
        unshared_fields (all records have unique value/array),
        array_specific_fields (any fields unique to array files, used mainly
        where dimensions may vary between records so the number to parse needs
        to be stored), and site_specific_fields (any fields unique to site
        files, used mainly where dimensions of flattened arrays need to be
        stored).
        """
        return {}

    @classmethod
    def unshared_fields_dims_site(cls):
        """
        Retrieve the fields of the format that belong in both site
        and array structured files as values that vary with record number.
        For every field, a function is given that calculates the
        dimensions for the site structured format.

        Returns
        -------
        Returns dictionary of Unshared field: dimensions per record in site
        structure. Unshared fields are not common across records. These
        dimensions can vary per record so the functions take the arrays data
        dictionary and the record number. This class method is used to convert
        from array structure to site structure.
        The unshared fields and the functions to generate their dimensions
        are unique to the format so should be overwritten by the child class.

        Notes
        -----
        All fields possible = single_element_types + array_dtypes
        Fields are then classified into four types to determine
        how to restructure: shared_fields (all records have the same value),
        unshared_fields (all records have unique value/array),
        array_specific_fields (any fields unique to array files, used mainly
        where dimensions may vary between records so the number to parse needs
        to be stored), and site_specific_fields (any fields unique to site
        files, used mainly where dimensions of flattened arrays need to be
        stored).
        """
        return {}

    @classmethod
    def array_specific_fields_generate(cls):
        """
        Retrieve the fields of the format that belong only in the array
        structured files. For every array specific field, a function
        is given that calculates the value for the array field.

        Returns
        -------
        A dictionary of any fields that are array specific or require
        specific function to generate. The key is the name of the array
        specific field and the value in the dictionary is the function that
        takes the records (site data dictionary) to generate the value for that
        field in the arrays format. This class method is used when
        restructuring from site to array style.
        The array specific fields and the functions to generate them are
        unique to the format so should be overwritten by the child class.

        Notes
        -----
        All fields possible = single_element_types + array_dtypes
        Fields are then classified into four types to determine
        how to restructure: shared_fields (all records have the same value),
        unshared_fields (all records have unique value/array),
        array_specific_fields (any fields unique to array files, used mainly
        where dimensions may vary between records so the number to parse needs
        to be stored), and site_specific_fields (any fields unique to site
        files, used mainly where dimensions of flattened arrays need to be
        stored).
        """
        return {}

    @classmethod
    def site_specific_fields_generate(cls):
        """
        Retrieve the fields of the format that belong only in the site
        structured files. For every site specific field, a function
        is given that calculates the value for the site field.

        Returns
        -------
        A dictionary of any fields that are site specific or require
        specific function to generate. The key is the name of the site
        specific field and the value in the dictionary is the function that
        takes the arrays (array data dictionary) and the record_num to
        generate the value for that field at that record number. This class
        method is used when restructuring from array to site style.
        The site specific fields and the functions to generate them are
        unique to the format so should be overwritten by the child class.

        Notes
        -----
        All fields possible = single_element_types + array_dtypes
        Fields are then classified into four types to determine
        how to restructure: shared_fields (all records have the same value),
        unshared_fields (all records have unique value/array),
        array_specific_fields (any fields unique to array files, used mainly
        where dimensions may vary between records so the number to parse needs
        to be stored), and site_specific_fields (any fields unique to site
        files, used mainly where dimensions of flattened arrays need to be
        stored).
        """
        return {}

    # STATIC METHODS THAT VARY BY FORMAT
    # i.e. methods used in restructuring that the format to/from site
    # structure for interpreting site data. These formats
    # exist blank here because the BaseFormat does not have any
    # fields that are flattened in the site array.

    @staticmethod
    def reshape_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        A function to reshape a record field if it has been flattened
        for storage in the site file (a common convention). The
        fields for reshaping and their dimensions are specific to the
        format. This is a necessary function for interpreting site data.

        Parameters
        ----------
        records
            site-style records dictionary.

        Returns
        -------
        records
            site-style records dictionary with any data field arrays reshaped
            as required by the format. The BaseFormat does not contain
            any fields that need to be reshaped but some child classes do.

        Notes
        -----
        This function is used in the _site_to_array restructuring which
        is common to all Borealis formats (a method of the BaseFormat).

        This reshapes them to the correct dimensions. Some formats may not
        have this issue, in which case this function does not need to be
        updated by the child class.
        """
        return records

    @staticmethod
    def flatten_site_arrays(records: OrderedDict) -> OrderedDict:
        """
        A function to flatten record fields if needed for storing in the
        site structure. The fields for flattening are specific to the
        format.

        Parameters
        ----------
        records
            An OrderedDict of the site style data, organized by record.
            Records are stored with timestamps as the keys and the data for
            that timestamp stored as a dictionary.

        Returns
        -------
        records
            An OrderedDict of the site style data, with any fields
            necessary in all records flattened as may be the convention
            in site structured files of that format.

        Notes
        -----
        This function is used by the _array_to_site class method
        in restructuring files. That method is common to all formats.

        This flattens the data correctly for the file format. Some formats
        may not have this issue, in which case this function does not need to
        be updated by the child class.
        """
        return records

    # CLASS METHODS COMMON ACROSS FORMATS
    # i.e. class methods that build off the other class methods so generally
    # do not need to be overwritten by the formats.

    @classmethod
    def unshared_fields(cls):
        """
        Compute the unshared field names.

        Returns
        -------
        A list of the unshared fields built from the
        unshared_fields_dims_array method which should specify all
        unshared fields.

        Notes
        -----
        All fields possible = single_element_types + array_dtypes
        Fields are then classified into four types to determine
        how to restructure: shared_fields (all records have the same value),
        unshared_fields (all records have unique value/array),
        array_specific_fields (any fields unique to array files, used mainly
        where dimensions may vary between records so the number to parse needs
        to be stored), and site_specific_fields (any fields unique to site
        files, used mainly where dimensions of flattened arrays need to be
        stored).
        """
        return list(cls.unshared_fields_dims_array().keys())

    @classmethod
    def array_specific_fields(cls):
        """
        Compute the array specific field names.

        Returns
        -------
        A list of the array specific fields built from the
        array_specific_fields_generate dictionary which should
        specify all array specific fields as keys.

        Notes
        -----
        All fields possible = single_element_types + array_dtypes
        Fields are then classified into four types to determine
        how to restructure: shared_fields (all records have the same value),
        unshared_fields (all records have unique value/array),
        array_specific_fields (any fields unique to array files, used mainly
        where dimensions may vary between records so the number to parse needs
        to be stored), and site_specific_fields (any fields unique to site
        files, used mainly where dimensions of flattened arrays need to be
        stored).
        """
        return list(cls.array_specific_fields_generate().keys())

    @classmethod
    def site_specific_fields(cls):
        """
        Compute the site specific field names.

        Returns
        -------
        A list of the site specific fields built from the
        array_specific_fields_generate dictionary which should
        specify all site specific fields as keys.

        Notes
        -----
        All fields possible = single_element_types + array_dtypes
        Fields are then classified into four types to determine
        how to restructure: shared_fields (all records have the same value),
        unshared_fields (all records have unique value/array),
        array_specific_fields (any fields unique to array files, used mainly
        where dimensions may vary between records so the number to parse needs
        to be stored), and site_specific_fields (any fields unique to site
        files, used mainly where dimensions of flattened arrays need to be
        stored).
        """
        return list(cls.site_specific_fields_generate().keys())

    @classmethod
    def site_fields(cls):
        """
        Compute all fields that belong in a site structured file.

        Returns
        -------
        A list of the field names that go into a site file of the format.
        This list is built from the shared_fields, unshared_fields, and
        site_specific fields. Together this should be all fields in a
        site structured file.

        Notes
        -----
        All fields possible = single_element_types + array_dtypes
        Fields are then classified into four types to determine
        how to restructure: shared_fields (all records have the same value),
        unshared_fields (all records have unique value/array),
        array_specific_fields (any fields unique to array files, used mainly
        where dimensions may vary between records so the number to parse needs
        to be stored), and site_specific_fields (any fields unique to site
        files, used mainly where dimensions of flattened arrays need to be
        stored).
        """
        return cls.shared_fields() + cls.unshared_fields() + \
            cls.site_specific_fields()

    @classmethod
    def array_fields(cls):
        """
        Compute all fields that belong in an array structured file.

        Returns
        -------
        A list of the field names that go into a array file of the format.
        This list is built from the shared_fields, unshared_fields, and
        array_specific fields. Together this should be all fields in a
        array structured file.

        Notes
        -----
        All fields possible = single_element_types + array_dtypes
        Fields are then classified into four types to determine
        how to restructure: shared_fields (all records have the same value),
        unshared_fields (all records have unique value/array),
        array_specific_fields (any fields unique to array files, used mainly
        where dimensions may vary between records so the number to parse needs
        to be stored), and site_specific_fields (any fields unique to site
        files, used mainly where dimensions of flattened arrays need to be
        stored).
        """
        return cls.shared_fields() + cls.unshared_fields() + \
            cls.array_specific_fields()

    @classmethod
    def site_single_element_fields(cls):
        """
        Compute the single element fields in the site structure.

        Returns
        -------
        A list of the site fields that should contain only a single
        element (versus an array).

        See Also
        --------
        site_fields
        single_element_types
        """
        return [k for k in cls.site_fields() if k in
                list(cls.single_element_types().keys())]

    @classmethod
    def site_single_element_types(cls):
        """
        Compute the single element fields and their types for site structure.

        Returns
        -------
        A dict of the site fields that should contain only a single
        element (versus an array), with their type.

        See Also
        --------
        site_fields
        single_element_types
        """
        return {k: cls.single_element_types()[k]
                for k in cls.site_single_element_fields()}

    @classmethod
    def site_array_dtypes_fields(cls):
        """
        Compute the fields in the site structure that should contain a numpy
        array.

        Returns
        -------
        A list of the site fields that should contain a numpy array of
        values in the record.

        See Also
        --------
        site_fields
        array_dtypes
        """
        return [k for k in cls.site_fields() if k in
                list(cls.array_dtypes().keys())]

    @classmethod
    def site_array_dtypes(cls):
        """
        Compute the fields in the site structure that should contain a numpy
        array and give the dtype for the array.

        Returns
        -------
        A dictionary of the site fields that should contain a numpy array of
        values in the record, and the dtype that should be in the array.

        See Also
        --------
        site_fields
        array_dtypes
        """
        return {k: cls.array_dtypes()[k] for k in
                cls.site_array_dtypes_fields()}

    @classmethod
    def array_single_element_fields(cls):
        """
        Compute the single element fields in the array structure.

        Returns
        -------
        A list of the array fields that should contain only a single
        element (versus an array).

        Notes
        -----
        Any single element field present in the array structured
        files must be a shared_field, otherwise it would be an array
        of dimension num_records and belong in the
        array_array_dtypes.

        See Also
        --------
        array_fields
        single_element_types
        """
        return [k for k in cls.array_fields() if
                k in list(cls.single_element_types().keys()) and k in
                cls.shared_fields()]

    @classmethod
    def array_single_element_types(cls):
        """
        Compute the single element fields and their types for array structure.

        Returns
        -------
        A dict of the array fields that should contain only a single
        element (versus an array), with their type.

        Notes
        -----
        Any single element field present in the array structured
        files must be a shared_field, otherwise it would be an array
        of dimension num_records and belong in the
        array_array_dtypes.

        See Also
        --------
        array_fields
        single_element_types
        """
        return {k: cls.single_element_types()[k]
                for k in cls.array_single_element_fields()}

    @classmethod
    def array_array_dtypes_fields(cls):
        """
        Compute the fields in the array structure that should contain a numpy
        array.

        Returns
        -------
        A list of the array fields that should contain a numpy array of
        values.

        Notes
        -----
        These fields can be from the single_element_types because those
        are listed per record. The array fields are given for all records,
        so any unshared field should be included here as it will be a numpy
        array with first dimension = num_records.

        See Also
        --------
        array_fields
        array_dtypes
        unshared_fields
        single_element_types
        array_specific_fields
        """
        return [k for k in cls.array_fields() if
                k in list(cls.array_dtypes().keys())] + \
               [k for k in cls.array_fields() if k in
                list(cls.single_element_types().keys()) and
                ((k in cls.unshared_fields()) or
                 (k in cls.array_specific_fields()))]

    @classmethod
    def array_array_dtypes(cls):
        """
        Compute the fields in the array structure that should contain a numpy
        array, and their dtype.

        Returns
        -------
        A dictionary of the array fields that should contain a numpy array of
        values, and the dtype of those values.

        Notes
        -----
        These fields can be from the single_element_types because those
        are listed per record. The array fields are given for all records,
        so any unshared field should be included here as it will be a numpy
        array with first dimension = num_records.

        See Also
        --------
        array_fields
        array_dtypes
        unshared_fields
        single_element_types
        array_specific_fields
        """
        array_array_dtypes = {k: cls.array_dtypes()[k] for k in
                              cls.array_array_dtypes_fields() if k in
                              list(cls.array_dtypes().keys())}

        array_array_dtypes.update(
            {k: cls.single_element_types()[k] for
             k in cls.array_array_dtypes_fields() if k in
             list(cls.single_element_types().keys())})

        return array_array_dtypes

    @classmethod
    def _site_to_array(cls, data_dict: OrderedDict) -> dict:
        """
        Base function for converting site Borealis data to
        restructured array format.

        Parameters
        ----------
        data_dict: OrderedDict
            a dict of timestamped records loaded from an hdf5 Borealis site
            file

        Returns
        -------
        new_data_dict
            A dictionary containing the data from data_dict
            reformatted to be stored entirely in array style, or as
            one entry if the field does not change between records.
            This means that for fields that change between records,
            the first dimension in the array will equal num_records
            (these are called unshared_fields). For fields common to all
            records, there will only be the one value that applies (these
            are known as shared_fields).

        See Also
        --------
        is_restructureable
        reshape_site_arrays
        shared_fields
        array_specific_fields_generate
        unshared_fields_dims_array

        Notes
        -----
        The results will differ based on the format class, as many of the
        class methods used inside this method should be specific
        to the format and updated in the child class. However, this is the
        process required for any restructuring, so this method itself should
        not be updated by the child class.
        """

        if not cls.is_restructureable():
            raise borealis_exceptions.BorealisRestructureError(
                'File format {} not recognized as '
                'restructureable from site to array style or vice versa.'
                ''.format(cls.__name__))

        new_data_dict = dict()
        num_records = len(data_dict)

        # some fields are linear in site style and need to be reshaped.
        data_dict = cls.reshape_site_arrays(data_dict)

        # write shared fields to dictionary
        first_key = list(data_dict.keys())[0]
        for field in cls.shared_fields():
            new_data_dict[field] = data_dict[first_key][field]

        # write array specific fields using the given functions.
        for field in cls.array_specific_fields():
            new_data_dict[field] = cls.array_specific_fields_generate(
                )[field](data_dict)

        # write the unshared fields, initializing empty arrays to start.
        temp_array_dict = dict()

        # get array dims of the unshared fields arrays
        field_dimensions = {}
        for field in cls.unshared_fields():
            dims = [dimension_function(data_dict) for
                    dimension_function in
                    cls.unshared_fields_dims_array()[field]]
            field_dimensions[field] = dims

        # all fields to become arrays
        for field, dims in field_dimensions.items():
            array_dims = [num_records] + dims
            array_dims = tuple(array_dims)

            if field in cls.single_element_types():
                datatype = cls.single_element_types()[field]
            else:  # field in array_dtypes
                datatype = cls.array_dtypes()[field]
            empty_array = np.empty(array_dims, dtype=datatype)
            # initialize all values to NaN; some indices may not be filled
            # do to dimensions that are max values (num sequences, etc can
            # change between records)
            empty_array[:] = np.NaN
            temp_array_dict[field] = empty_array

        # iterate through the records, filling the unshared and array only
        # fields
        for rec_idx, k in enumerate(data_dict.keys()):
            for field in cls.unshared_fields():  # all unshared fields
                empty_array = temp_array_dict[field]
                if type(data_dict[first_key][field]) == np.ndarray:
                    # only fill the correct length, appended NaNs occur for
                    # dims with a determined max value
                    data_buffer = data_dict[k][field]
                    buffer_shape = data_buffer.shape
                    index_slice = [slice(0, i) for i in buffer_shape]
                    # insert record index at start of array's slice list
                    index_slice.insert(0, rec_idx)
                    index_slice = tuple(index_slice)
                    # place data buffer in the correct place
                    empty_array[index_slice] = data_buffer
                else:  # not an array, num_records is the only dimension
                    empty_array[rec_idx] = data_dict[k][field]

        new_data_dict.update(temp_array_dict)

        return new_data_dict

    @classmethod
    def _array_to_site(cls, data_dict: dict) -> OrderedDict:
        """
        Base function for converting array Borealis data to
        site format.

        Parameters
        ----------
        data_dict: dictionary of array restructured Borealis data.

        Returns
        -------
        new_data_dict
            An OrderedDict of timestamped records as if loaded from
            the original site file.

        See Also
        --------
        is_restructureable
        flatten_site_arrays
        shared_fields
        site_specific_fields_generate
        unshared_fields_dims_site

        Notes
        -----
        The results will differ based on the format class, as many of the
        class methods used inside this method should be specific
        to the format and updated in the child class. However, this is the
        process required for any restructuring, so this method itself should
        not be updated by the child class.
        """

        if not cls.is_restructureable():
            raise borealis_exceptions.BorealisRestructureError(
                'File format {} not recognized as '
                'restructureable from site to array style or vice versa.'
                ''.format(cls.__name__))

        timestamp_dict = OrderedDict()
        for record_num, seq_timestamp in \
                enumerate(data_dict["sqn_timestamps"]):
            # format dictionary key in the same way it is done
            # in datawrite on site
            seq_datetime = datetime.utcfromtimestamp(seq_timestamp[0])
            epoch = datetime.utcfromtimestamp(0)
            key = str(int((seq_datetime - epoch).total_seconds() * 1000))

            timestamp_dict[key] = dict()
            # populate shared fields in each record,
            for field in cls.shared_fields():
                timestamp_dict[key][field] = data_dict[field]

            # populate site specific fields using given functions
            # that take both the arrays data and the record number
            for field in cls.site_specific_fields():
                timestamp_dict[key][field] = cls.site_specific_fields_generate(
                    )[field](data_dict, record_num)

            for field in cls.unshared_fields():
                if field in cls.single_element_types():
                    datatype = cls.single_element_types()[field]
                    # field is not an array, single element per record.
                    # unshared_field_dims_site should give empty list.
                    timestamp_dict[key][field] = datatype(data_dict[field]
                                                          [record_num])
                else:  # field in array_dtypes
                    datatype = cls.array_dtypes()[field]
                    # need to get the dims correct, not always equal to the max
                    site_dims = [dimension_function(data_dict, record_num)
                                 for dimension_function in
                                 cls.unshared_fields_dims_site()[field]]
                    index_slice = [slice(0, i) for i in site_dims]
                    index_slice.insert(0, record_num)
                    index_slice = tuple(index_slice)
                    timestamp_dict[key][field] = data_dict[field][index_slice]

        timestamp_dict = cls.flatten_site_arrays(timestamp_dict)

        return timestamp_dict

    # STATIC METHODS COMMON ACROSS FORMATS
    # i.e. common methods that can be used by multiple formats in restructuring
    # (generally these will be used in the unshared fields dims for arrays)

    @staticmethod
    def find_max_sequences(records: OrderedDict) -> int:
        """
        Finds the maximum number of sequences between records in a Borealis
        site style records file.

        Parameters
        ----------
        records
            Site formatted records from a Borealis file, organized as one
            record for each slice

        Returns
        -------
        max_seqs
            The largest number of sequences found in one record from the
            file

        Notes
        -----
        Used by unshared_fields_array_dims functions if the number of
        sequences is a dimension of the per-record array.
        """
        max_seqs = 0
        for k in records:
            if max_seqs < records[k]["num_sequences"]:
                max_seqs = records[k]["num_sequences"]
        return max_seqs

    @staticmethod
    def find_max_beams(records: OrderedDict) -> int:
        """
        Finds the maximum number of beams between records in a Borealis
        site style records file.

        Parameters
        ----------
        records
            Site formatted records from a Borealis file, organized as one
            record for each slice

        Returns
        -------
        max_beams
            The largest number of beams found in one record from the
            file

        Notes
        -----
        Used by unshared_fields_array_dims functions if the number of
        beams is a dimension of the per-record array.
        """
        max_beams = 0
        for k in records:
            if max_beams < len(records[k]["beam_nums"]):
                max_beams = len(records[k]["beam_nums"])
        return max_beams

    @staticmethod
    def find_max_blanked_samples(records: OrderedDict) -> int:
        """
        Finds the maximum number of blanked samples between records in a
        Borealis site style records file.

        Parameters
        ----------
        records
            Site formatted records from a Borealis file, organized as one
            record for each slice

        Returns
        -------
        max_beams
            The largest number of beams found in one record from the
            file

        Notes
        -----
        Used by unshared_fields_array_dims functions if the number of
        blanked_samples is a dimension of the per-record array.
        """
        max_blanked_samples = 0
        for k in records:
            if max_blanked_samples < len(records[k]["blanked_samples"]):
                max_blanked_samples = len(records[k]["blanked_samples"])
        return max_blanked_samples
