import os
import matplotlib.pyplot as plt
import numpy as np
import readers
import calculators
import plotters
import functions
import run_detection
from pathlib import Path

savedata        = False     # whether or not the gaze events and their measures are saved in .csv files
showfig         = True      # whether or not the plot figures are shown after detection
savefig         = False     # whether or not the plot figures are saved after detection
debugdetection  = False     # show runtime info about the detection in the console
printresults    = True      # show results of the detection in the console

# Import csv files --------------------------------------------------------------------------------------------------
datapath        = os.getcwd() + "/testdata/"    # put the full path to your data here
participants    = 2                             # number of participants
trials          = 2                             # trials per participant
filename        = 'varjo_gaze_output'           # looks for files with this string in the name

for participant in range(1, participants + 1):
    print(), print(), print('Analyisis results for participant {}'.format(participant))
    #start plot
    fig, axs = plt.subplots(trials, figsize=[25.60, 7.20*trials])
    fig.suptitle('Detection per trial for participant {}'.format(participant))

    for trial in range(1, trials + 1):
        trialpath = datapath + '{}/{}/'.format(participant,trial)

        print(), print('Trial ' + str(trial))
        gazedata  = readers.Gaze(datapath, participant, trial, filename)
        pupildata = readers.Pupil(datapath, participant, trial, filename)
        focusdata = readers.Focus(datapath, participant, trial, filename)

# classify gaze events ----------------------------------------------------------------------------------------------
        classifiedgazedata = run_detection.DetectGazeEvents(gazedata, debugdetection)

        t = classifiedgazedata['data']['time'] / 1000           # [s]
        x = classifiedgazedata['data']['x']                     # [deg]
        y = classifiedgazedata['data']['y']                     # [deg]
        v = classifiedgazedata['data']['v']                     # [deg/s]
        e = classifiedgazedata['data']['EYE_MOVEMENT_TYPE']     # ('UNKNOWN', 'FIX', 'SACCADE', 'SP', 'NOISE', 'BLINK', 'NOISE_CLUSTER', 'PSO')

        dt = 1000 / np.mean(np.diff(classifiedgazedata['data']['time']))
        print("Gaze data recorded at: {} Hz".format(dt))

# Analyzing gaze event measures --------------------------------------------------------------------------------------
        Fixations = calculators.fixation(x, y, t, e, printresults)
        Saccades  = calculators.saccade(x, y, v, t, e, printresults)
        Pursuits  = calculators.pursuit(x, y, v, t, e, printresults)
        Blinks    = calculators.blink(t, e, printresults)

# Saving gaze event data ---------------------------------------------------------------------------------------------
        if savedata:
            outputpath = trialpath + 'detection'
            Path(outputpath).mkdir(parents=True, exist_ok=True)
            # save detections per even type with their measures
            functions.save_events(Fixations, 'fixations.csv', outputpath)
            functions.save_events(Saccades, 'saccades.csv', outputpath)
            functions.save_events(Pursuits, 'pursuits.csv', outputpath)
            functions.save_events(Blinks, 'blinks.csv', outputpath)
            # add gaze_event classification column to raw data and save copy
            csvdata = readers.file_reader(datapath, participant, trial, filename)
            csvdata["gaze_event"] = classifiedgazedata['data']['EYE_MOVEMENT_TYPE']
            csvdata.to_csv(outputpath + "/classified_data.csv")

# Plotting and saving------------------------------------------------------------------------------------------------
        plotters.detection(x, y, t, v, Fixations, Saccades, Pursuits, Blinks, trials, trial, axs)
        plotters.calculation(Fixations, Saccades, Pursuits, Blinks, trial, participant)
        outputpath = trialpath + "calculation-p{}-t{}.png".format(participant, trial, participant, trial)
        if savefig: plt.savefig(outputpath, bbox_inches='tight')

    plt.figure(1)
    outputpath = datapath + '{}/detection-p{}.png'.format(participant, participant)
    if savefig: plt.savefig(outputpath, bbox_inches='tight')
    if showfig: plt.show()
    if savefig: plt.close('all')


