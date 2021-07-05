from collections import OrderedDict
import arff
import warnings
import numpy as np
import numpy.lib.recfunctions as rfn

class ArffHelper(object):
    """
    The class is based on general arff handler with an extra keyword %@METADATA
    (they are comment lines in the description, i.e. lines *before* the
    `relation` keyword).

    Metadata fields contains metadata names and related values (separated by space characters).

    - Lines starting with "%" are comments, except for line starting with %@METADATA
    - Lines starting with "@" that is followed by a word (without space), are considered
      keywords. The available keywords are the following:
        @RELATION: a string with the name of the data set.
        @ATTRIBUTES: a list of attributes representing names of data columns
                     followed by the types of data. The available data types
                     are 'NUMERIC', 'REAL', 'INTEGER' or a list of string.
        @DESCRIPTION: a string with the description of the data set.
        @DATA: a list of data instances. The data should follow the order that
               the attributes were presented.
    - Metadata ('%@METADATA <KEY> <VALUE>' lines) can have any keys, but is not currently used

    """
    _METADATA_STRING = '@metadata'
    _METADATA_COLUMNS_COUNT = 3  # @METADATA KEY VALUE
    _METADATA_KEY_COLUMN = 1     # First key,
    _METADATA_VALUE_COLUMN = 2   # then value
    _ATTRIBUTES_TYPE = {'NUMERIC': np.float32, 'REAL': np.double, 'INTEGER': np.int64}

    def __init__(self):
        pass

    # Public interface functions (I/O)
    #
    # I. Loading functions (from file or string)
    #

    @staticmethod
    def add_column(obj, name, dtype, default_value):
        """
        Add a new column to @obj['data'] and a new attribute to @obj['attributes']
        (i.e. the name of the new column and the data type for this column).
        This operation is performed in-place, so the @obj itself is changed.

        :param obj: arff object before adding new column.
        :param name: name of the new column.
        :param dtype: data type of the new column.
                      Available data types:
                      'NUMERIC', 'REAL', 'INTEGER' or a list of strings (then it's a categorical column with
                      the provided values as options).
        :param default_value: default value of the new column (we need to somehow assign the data in the new column).
        :return: arff object with an additional column.

        """
        obj['data'] = ArffHelper.add_column_to_array(obj['data'], name, dtype, default_value)
        obj['attributes'].append((name, dtype))

        return obj

    @staticmethod
    def add_column_to_array(arr, name, dtype, def_value):
        """
        Add a new column to a structured numpy array.

        :param arr: numpy array before adding column.
        :param name: name of the new column.
        :param dtype: data type of the new column.
                      Available data types:
                      'NUMERIC', 'REAL', 'INTEGER' or a list of strings (then it's a categorical column with
                      the provided values as options).
        :param def_value: default value of the new column.
        :return: numpy array with new column.

        """
        # check if def_value is in dtype
        if type(def_value) == str and def_value not in dtype:
            warnings.warn("The type of the default value is not the same as type of column data"
                          " or the default value is not in the list (date type provided is {})".format(name))

        if name in arr.dtype.names:
            raise ValueError('Array @arr already has a field {}'.format(name))

        if arr.size != 0:
            arr = rfn.append_fields(base=arr,
                                    names=name,
                                    data=[def_value] * len(arr),
                                    dtypes=ArffHelper._convert_dtype_to_numpy(dtype),
                                    usemask=False)
        else:
            # If @arr is empty, it should have been created with ArffHelper.create_empty() method, or in a similar
            # fashion. In that case, it has a length (passed as a parameter at creation), but no elements.
            arr = np.array([def_value] * len(arr), dtype=[(name, ArffHelper._convert_dtype_to_numpy(dtype))])
        return arr

    @staticmethod
    def remove_column(obj, name):
        """
        Remove a column with respective name from @obj['data'] and its attributes (@obj['attributes']).

        :param obj: arff object before adding new column.
        :param name: name of the deleted column.
        :return: arff object without the column @name.

        """
        deleted_column_index = [column_name for column_name, _ in obj['attributes']].index(name)
        obj['attributes'].pop(deleted_column_index)
        # keep just the remaining attributes
        obj['data'] = rfn.drop_fields(base=obj['data'],
                                      drop_names=name,
                                      usemask=False)
        return obj

    @staticmethod
    def convert_data_to_structured_array(obj):
        """
        Convert data in @obj['data'] into a structured numpy array according to the data type in
        @obj['attributes'].

        :param obj: arff object before data conversion.
        :return: arff object after data conversion.

        """
        d = np.dtype([(str(at[0]), ArffHelper._convert_dtype_to_numpy(at[1])) for at in obj['attributes']])
        obj['data'] = np.array([tuple(item) for item in obj['data']], dtype=d)
        return obj

    @staticmethod
    def _convert_dtype_to_numpy(data_type):
        """
        Validate input @data_type as ARFF-supported data type and convert to numpy.dtype.

        :param data_type: input data_type, string.
                          Available data types:
                          'NUMERIC', 'REAL', 'INTEGER' or a tuple of string (then it's a categorical attribute).
        :return: converted numpy.dtype from input data_type.

        """
        if data_type in ArffHelper._ATTRIBUTES_TYPE.keys():
            return ArffHelper._ATTRIBUTES_TYPE[data_type]
        else:
            if type(data_type) == tuple:
                max_length = max(map(len, data_type))
            else:
                raise ValueError("Wrong data type in attributes. "
                                 "It should be a list of strings or one of the data types in {}".format(
                                  ', '.join(ArffHelper._ATTRIBUTES_TYPE.keys())))

            return '<U{}'.format(max_length)
