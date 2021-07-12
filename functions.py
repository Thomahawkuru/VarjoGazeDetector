import numpy as np
from arff_helper import ArffHelper
from collections import OrderedDict

"""
Various helper functions needed for rest of the code
"""

def load_CSV_as_arff_object(x, y, t, s, fname):
    """
    Load data from the given input .csv file and return an arff object.
    This is a "model" function for writing new data adapters. To create a similarly-functioning method,
    one would need to parse the file under @fname to extract an an arff object (dictionary with special keys)
    ofr the following structure:

    arff_obj = {
        'relation': 'gaze_recording',
        'description': '',
        'data': [],
        'metadata': {},
        'attributes': [('time', 'NUMERIC'),
                       ('x', 'NUMERIC'),
                       ('y', 'NUMERIC'),
                       ('v', 'NUMERIC'),
                       ('status', 'INTEGER')]},
    and fill in its fields.

    'data' should first contain a numpy list of lists (the latter lists should be of the same length as 'attributes'.
    'description' is just a string that gets put into the beginning of the file.
    'metadata' is empty
    'attributes' (if additional ones are required) is a list of tuples, each tuple consisting of 2 elements:
        - attribute name
        - attribute type, can be INTEGER (=int64), NUMERIC (=float32), REAL (=double), or a list of strings, which
          means it is a categorical attribute and only these values are accepted.

    After 'data' is filled with appropriate lists of values, call
    >> arff_obj = ArffHelper.convert_data_to_structured_array(arff_obj)
    to (unsurprisingly) convert the data in @arff_obj['data'] into a structured numpy array for easier data access.

    :param fname: name of .csv file.
    :return: an arff object with keywords:
             "@RELATION, @DESCRIPTION, @DATA, @ATTRIBUTES".
    """

    COMMENT_PREFIX = '#'
    # the 'gaze ... ...' line has this many "fields" (defines the video resolution)
    GAZE_FORMAT_FIELD_COUNT = 0
    # Samples are in lines that look like <timestamp> <x> <y> <confidence>.
    # In case of binocular tracking, these are the mean coordinates of the two eyes anyway.
    GAZE_SAMPLE_FIELDS = 3

    arff_obj = {
        'relation': 'gaze_recording',
        'description': [],
        'data': [],
        'metadata': OrderedDict(),
        'attributes': [('time', 'NUMERIC'),
                       ('x', 'NUMERIC'),
                       ('y', 'NUMERIC'),
                       ('status', 'INTEGER')]
    }

    description = ""
    data = np.array([t, x, y, s])
    arff_obj['data'] = np.array([tuple(item) for item in np.transpose(data)])
    arff_obj['metadata']['filename'] = fname
    arff_obj['description'] = '\n'.join(description)

    arff_obj = ArffHelper.convert_data_to_structured_array(arff_obj)

    # add velocity type attribute
    arff_obj = ArffHelper.add_column(arff_obj, 'v', 'NUMERIC', 0.0)

    # add eye movement type attribute
    EVENTS = ('UNKNOWN', 'FIX', 'SACCADE', 'SP', 'NOISE', 'BLINK', 'NOISE_CLUSTER', 'PSO')
    arff_obj = ArffHelper.add_column(arff_obj, 'EYE_MOVEMENT_TYPE', EVENTS, EVENTS[0])

    return arff_obj

def get_xy_moving_average(data, window_size, inplace=False):
    """
    Get moving average of 'x', 'y' columns of input data (the moving window is centered around the data point).

    Some data at the beginning and in the end will be left unchanged (where the window does not fit fully).
    Thus the length of offset is equal to (window_size - 1)/2.
    The rest of data will be replaced with central moving average method.

    :param data: structured numpy array that contains columns 'x' and 'y'.
    :param window_size: width of moving average calculation.
    :param inplace: whether to replace input data with processed data (False by default)
    :return: data set with moving average applied to 'x' and 'y' columns.

    """
    assert window_size % 2 == 1, "The @normalization_sliding_window_size_samples parameter is set to {}, but it " \
                                 "has to be odd, so that we can centre the moving window around the current sample.".\
        format(window_size)
    if not inplace:
        data = data.copy()
    offset = int((window_size - 1) / 2)
    for column in ['x', 'y']:
        res = np.cumsum(data[column], dtype=float)
        res[window_size:] = res[window_size:] - res[:-window_size]
        res = res[window_size - 1:] / window_size
        if offset > 0:
            data[column][offset:-offset] = res
        else:
            data[column][:] = res
    return data

def fill_blink_gaps(Tx, Ty, t, s):
    """
    Find gaps in the data that represent blinks, for recordings with Varjo Base.

    In Unity recording, a blink period is recorded with zeros. This is how blinks are detected.
    Varjo base does not record any data during a blink, so instead a jump in time-interval is found.
    This funcition detects those gaps in the data and fills them with zero arrays for blink detection.

    :param Tx: numpy array with 'x' data in deg
    :param Ty: numpy array with 'y' data in deg
    :param t: numpy array with timestamps
    :param s: numpy array with gaze tatus

    :return: data set Tx, Ty, t, s with added interpolations where blinks occured

    """
    # find blinks for Varjo base recording by gaps in time array
    dt = np.diff(t)
    blink_onsets = np.nonzero(dt > 30)[0]
    blink_offsets = np.array([blink + 1 for blink in blink_onsets])

    #interpolate for each gap the x, y ,t and s data
    if min(s) != 0:
        shift = 0
        for onset, offset in zip(blink_onsets, blink_offsets):
            onset  += shift
            offset += shift

            gaptime = t[offset] - t[onset]
            npoints = int(gaptime/dt.mean())

            # create patches
            timepatch  = np.linspace(t[onset], t[offset], npoints+2)
            timepatch = timepatch[1:-1]
            datapatch  = np.zeros(npoints)

            # append the patches in the data arrays
            t  = np.insert(t,  onset+1, timepatch)
            Tx = np.insert(Tx, onset+1, datapatch)
            Ty = np.insert(Ty, onset+1, datapatch)
            s  = np.insert(s,  onset+1, datapatch)

            # shift indexes with patch length
            shift += npoints

    return Tx, Ty, t, s

def save_events(data, fname, datapath):
    """
        saves detections and their measures csv files (fixations, saccades, pursuits and blinks).
        Each row of the csv, is one gaze event. It includes measures such as :
        ["t_start", 't_end', 'duration', 'x_start', 'y_start', 'x_end', 'y_end', 'amplitude', 'mean_vel', 'max_vel']

        :param data: data to save in the .csv
        :param fname: filename for the created .csv
        :param datapath: path to save the created .csv

    """
    allnames = ["t_start", 't_end', 'duration', 'x_start', 'y_start', 'x_end', 'y_end', 'amplitude', 'mean_vel', 'max_vel']
    names = allnames[0:len(data[1, :])]
    delimiter = ','
    header = delimiter.join(names)

    np.savetxt(datapath + '/' + fname, data, delimiter=delimiter, header=header, comments='')

def save_classification(gazedata):
    """
        saves the calssification and timeline to a csv files.
        Each row of the csv, is one gaze event. It includes measures such as :
        ["t_start", 't_end', 'duration', 'x_start', 'y_start', 'x_end', 'y_end', 'amplitude', 'mean_vel', 'max_vel']

        :param data: data to save in the .csv
        :param fname: filename for the created .csv
        :param datapath: path to save the created .csv

    """
