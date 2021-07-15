import os
import pandas
import math
import functions
import numpy as np


def file_reader(path, participant, trial, filename):
    # read data file
    file = [i for i in os.listdir(path) if os.path.isfile(os.path.join(path, i)) and \
            filename in i]
    csvdata = pandas.read_csv(path + file[0], delimiter=',')

    # remove last row (can be partially logged) and replace nan values
    csvdata.drop(csvdata.tail(1).index,inplace=True)
    csvdata.dropna(subset=["raw_timestamp"], inplace=True)
    if 'relative_to_video_first_frame_timestamp' in csvdata.columns:
        csvdata.dropna(subset=["relative_to_video_first_frame_timestamp"], inplace=True)
    csvdata = csvdata.fillna(0)

    # interpolate missing gaps in the data that represent Blinks (for Varjo Base recordings)
    patched_data = functions.fill_blink_gaps(csvdata)

    return patched_data

def gaze_arff(csvdata):

    # Raw Gaze data
    s = np.array(csvdata['status'])
    x = np.array(csvdata['gaze_forward_x'])
    y = np.array(csvdata['gaze_forward_y'])

    # get time stamps, checks wether or not a video time stamp is available
    if 'relative_to_video_first_frame_timestamp' in csvdata.columns:
        t = np.array(csvdata['relative_to_video_first_frame_timestamp'] / 10 ** 6)
    else:
        t = csvdata['raw_timestamp'] / 10 ** 6
        t = np.array(t - t[0])

    # convert to angles in deg
    Tx = (180 / math.pi) * np.arcsin(x)
    Ty = (180 / math.pi) * np.arcsin(y)

    #convert data tor arff object for processing
    gaze_points = functions.load_CSV_as_arff_object(Tx, Ty, t, s, '')

    return gaze_points

