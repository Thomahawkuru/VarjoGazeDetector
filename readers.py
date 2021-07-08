import os
import pandas
import math
import functions
import numpy as np


def file_reader(path, participant, trail, filename):
    # read data file
    path = path + str(participant) + "/" + str(trail) + "/"
    file = [i for i in os.listdir(path) if os.path.isfile(os.path.join(path, i)) and \
            filename in i]

    csvdata = pandas.read_csv(path + file[0], delimiter=',')

    return csvdata

def Gaze(path, participant, trail, filename):

    gazeData = file_reader(path, participant, trail, filename)
    fname = "P" + str(participant) + "_T" + str(trail)

    # Raw Gaze data
    s = np.array(gazeData['status'])
    x = np.array(gazeData['gaze_forward_x'])
    y = np.array(gazeData['gaze_forward_y'])

    # get time stamps, checks wether or not a video time stamp is available
    if 'relative_to_video_first_frame_timestamp' in gazeData.columns:
        t = np.array(gazeData['relative_to_video_first_frame_timestamp'] / 10 ** 6)
    else:
        t = gazeData['raw_timestamp'] / 10 ** 6
        t = np.array(t - t[0])

    # convert to angles in deg
    Tx = (180 / math.pi) * np.arcsin(x)
    Ty = (180 / math.pi) * np.arcsin(y)

    # interpolate missing gaps in the data that represent Blinks (for Varjo Base recordings)
    [Tx, Ty, t, s,] = functions.fill_blink_gaps(Tx, Ty, t, s)

    #convert data tor arff object for processing
    gaze_points = functions.load_CSV_as_arff_object(Tx, Ty, t, s, fname)

    return gaze_points

def Pupil(path, participant, trail, filename):

    gazeData = file_reader(path, participant, trail, filename)

    left = np.array(gazeData['left_pupil_size'])
    right = np.array(gazeData['right_pupil_size'])

    return left, right

def Focus(path, participant, trail, filename):

    gazeData = file_reader(path, participant, trail, filename)
    focus = np.array(gazeData['focus_distance'])

    return focus
