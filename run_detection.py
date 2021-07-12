from saccade_detector import SaccadeDetector
from blink_detector import BlinkDetector
from fixation_detector import FixationDetector
from sp_detector import SmoothPursuitDetector

# Notes on the detectors:
# (1) The saccade and blink detectors are quite robust together, their parameters are probably best left default, unless
# there is a specific reason to change them.
# (2) The balance between precision and recall of SP is currently shifted towards precision: we want to be sure that
# what we almost as SP, mostly is, while detecting a decent part of the real SP. If your priorities diverge from this,
# you should adjust the parameters of the SmoothPursuitDetector, relaxing the thresholds a bit, as well as
# the parameters of the FixationDetector, since most of the recall loss actually happens there.
# There you can try to relax the "prefiltering_interval_spread_threshold_degrees", "speed_threshold_degrees_per_sec" and
# "min_sp_duration_millisec" parers.

def DetectGazeEvents(gazedata, verbose):
    # Saccade Detection --------------------------------------------------------------------------------------------------
    sacparam = dict()
    sacparam["THRESHOLD_ONSET_FAST_DEGREE_PER_SEC"] = 137.5  # deg/s
    sacparam["THRESHOLD_ONSET_SLOW_DEGREE_PER_SEC"] = 17.1875  # deg/s
    sacparam["THRESHOLD_OFFSET_DEGREE_PER_SEC"] = 17.1875  # deg/s
    sacparam["MAX_SPEED_DEGREE_PER_SEC"] = 1031.25  # deg/s
    sacparam["MIN_DURATION_MILLISEC"] = 15  # milliseconds
    sacparam["MAX_DURATION_MILLISEC"] = 160  # milliseconds
    sacparam["VELOCITY_INTEGRAL_INTERVAL_MILLISEC"] = 4  # milliseconds
    sacparam["VERBOSE"] = verbose  # debug mode
    gazedata = SaccadeDetector(sacparam, gazedata)

    # Blink detection----------------------------------------------------------------------------------------------------
    blkparam = dict()
    blkparam['MINIMAL_BLINK_DURATION_MILLISEC'] = 20 # milliseconds
    blkparam["MAXIMAL_DISTANCE_TO_SACCADE_MILLISEC"] = 25  # milliseconds
    blkparam["VERBOSE"] = verbose
    gazedata = BlinkDetector(blkparam, gazedata)

    # Fixation detection-------------------------------------------------------------------------------------------------
    fixparam = dict()
    fixparam["PREFILTERING_INTERVAL_SPREAD_THRESHOLD_DEGREES"] = 1.4142135623730951  # deg
    fixparam["MIN_SP_DURATION_MILLISEC"] = 141.42135623730952  # milliseconds
    fixparam["SLIDING_WINDOW_WIDTH_MILLISEC"] = 100  # milliseconds
    fixparam["NORMALIZATION_SLIDING_WINDOW_SIZE_SAMPLES"] = 5  # n samples
    fixparam["SPEED_THRESHOLD_DEGREES_PER_SEC"] = 2  # deg/s
    fixparam["SLIDING_WINDOW_CRITERION"] = 'speed'  # 'speed' or 'spread'
    fixparam["INTERSACCADIC_INTERVAL_DURATION_THRESHOLD_MILLISEC"] = 75  # milliseconds
    fixparam["VERBOSE"] = verbose  # debug mode
    gazedata = FixationDetector(fixparam, gazedata)

    # Smooth Pursuit detection-------------------------------------------------------------------------------------------
    SPparam = dict()
    SPparam["MIN_PTS"] = 1  # minimum points for a neighborhood (default value, e.g. 160) * (N_observers / 46.9) * (F_hz / 250)
    SPparam["EPS_DEG"] = 4  # deg
    SPparam["TIME_SLICE_MILLISEC"] = 80  # milliseconds
    SPparam["VERBOSE"] = verbose  # debug mode

    sp_detector = SmoothPursuitDetector(param=SPparam)
    classifiedgazedata = sp_detector.detect(gaze_points_list=gazedata)

    return classifiedgazedata

# DEFAULT PARAMETERS
#
#     "SaccadeDetector": {
#         "threshold_onset_fast_degree_per_sec": 137.5
#         "threshold_onset_slow_degree_per_sec": 17.1875
#         "threshold_offset_degree_per_sec": 17.1875
#         "max_speed_degree_per_sec": 1031.25
#         "min_duration_millisec": 15
#         "max_duration_millisec": 160
#         "velocity_integral_interval_millisec": 4
#
#     "BlinkDetector": {
#         "minimal_blink_duration_millisec" = 10
#         "max_distance_to_saccade_millisec": 25
#
#     "FixationDetector": {
#         "prefiltering_interval_spread_threshold_degrees": 1.4142135623730951
#         "min_sp_duration_millisec": 141.42135623730952,
#         "sliding_window_width_millisec": 100
#         "normalization_sliding_window_size_samples": 5
#         "speed_threshold_degrees_per_sec": 2.0
#         "sliding_window_criterion": "speed"
#         "intersaccadic_interval_duration_threshold_millisec": 75
#
#     "SmoothPursuitDetector": {
#         "min_pts": 1,
#         "eps_deg": 4.0,
#         "time_slice_millisec": 80
