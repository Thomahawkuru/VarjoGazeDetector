import os
import matplotlib.pyplot as plt
import numpy as np
import readers
import calculators
import plotters
import functions
import run_detection
from pathlib import Path

savedata    = True
showfig     = False
savefig     = True
debugging   = False

# Import csv files --------------------------------------------------------------------------------------------------
datapath = os.getcwd() + "/testdata/"  # put the path to your data here
participants = 2  # number of participants
trails = 2  # trails per participant
filename = 'varjo_gaze_output'  # + date (automatically added)

for participant in range(1, participants + 1):
    print()
    print()
    print('Analyisis results for participant {}'.format(participant))
    #start plot
    fig, axs = plt.subplots(trails, figsize=[25.60, 7.20*trails])
    fig.suptitle('Detection per trail for participant {}'.format(participant))

    for trail in range(1, trails + 1):
        trailpath = datapath + '{}/{}/'.format(participant,trail)
        print()
        print('Trail ' + str(trail))
        gazedata = readers.Gaze(datapath, participant, trail, filename)
        pupildata = readers.Pupil(datapath, participant, trail, filename)
        focusdata = readers.Focus(datapath, participant, trail, filename)

# classify gaze events ----------------------------------------------------------------------------------------------
        classifiedgazedata = run_detection.DetectGazeEvents(gazedata, debugging)

        t = classifiedgazedata['data']['time'] / 1000  # [s]
        x = classifiedgazedata['data']['x']  # [deg]
        y = classifiedgazedata['data']['y']  # [deg]
        v = classifiedgazedata['data']['v']  # [deg/s]
        e = classifiedgazedata['data']['EYE_MOVEMENT_TYPE']  # ('UNKNOWN', 'FIX', 'SACCADE', 'SP', 'NOISE', 'BLINK', 'NOISE_CLUSTER', 'PSO')

        dt = 1000 / np.mean(np.diff(classifiedgazedata['data']['time']))
        print("Gaze data recorded at: {} Hz".format(dt))

# Analyzing and saving ----------------------------------------------------------------------------------------------
        Fixations = calculators.fixation(x, y, t, e)
        Saccades = calculators.saccade(x, y, v, t, e)
        Persuits = calculators.persuit(x, y, v, t, e)
        Blinks = calculators.blink(t, e)

        if savedata:
            outputpath = trailpath + 'detection'
            Path(outputpath).mkdir(parents=True, exist_ok=True)

            functions.save_csv(Fixations, 'fixations.csv', outputpath)
            functions.save_csv(Saccades, 'saccades.csv', outputpath)
            functions.save_csv(Persuits, 'persuits.csv', outputpath)
            functions.save_csv(Blinks, 'blinks.csv', outputpath)

# Plotting and saving------------------------------------------------------------------------------------------------
        plotters.detection(x, y, t, v, Fixations, Saccades, Persuits, Blinks, trail, axs)
        plotters.calculation(Fixations, Saccades, Persuits, Blinks, trail, participant)
        outputpath = trailpath + "calculation-p{}-t{}.png".format(participant, trail, participant, trail)
        if savefig: plt.savefig(outputpath, bbox_inches='tight')

    plt.figure(1)
    outputpath = datapath + '{}/detection-p{}.png'.format(participant, participant)
    if savefig: plt.savefig(outputpath, bbox_inches='tight')
    if showfig: plt.show()
    plt.close(plt.figure(1))


