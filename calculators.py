import numpy
import numpy as np


def fixation(x, y, time, events, printing):
    """Calculate fixation measures
	
	arguments
	time		-	numpy array of EyeTribe timestamps
	events      -   numpy array of of detected gaze events

	returns
				Fixations	-	list of lists, each containing [starttime, endtime, duration, endx, endy]
	"""

    # empty list to contain data
    Fixations = []

    # check where the missing samples are
    idx = numpy.array(events == 'FIX', dtype=int)

    # check where the starts and ends are (+1 to counteract shift to left)
    diff = numpy.diff(idx)
    starts = numpy.where(diff == 1)[0] + 1
    ends = numpy.where(diff == -1)[0] + 1

    # delete detected starts and ends from before and after recording
    if idx[-0] == 1:
        starts = starts[0:-1]
    if idx[0] == 1:
        ends = ends[1::]
    if len(starts) > len(ends):
        ends = np.append(ends, len(idx) - 1)

    # compile fixation starts and ends
    for i in range(len(starts)):
        # get starting index
        s = starts[i]
        # get ending index
        if i < len(ends):
            e = ends[i]
        elif len(ends) > 0:
            e = ends[-1]
        else:
            e = -1

        # add ending time
        xpos = np.mean([x[s], x[e]])
        ypos = np.mean([y[s], y[e]])
        duration = time[e] - time[s]
        Fixations.append([time[s], time[e], duration, xpos, ypos])

    Fixations = numpy.array(Fixations)
    if Fixations.any() and printing:
        numFix = len(Fixations)
        avgFix = 1000 * sum(Fixations[:, 2]) / numFix
        print('Number of fixations: ' + str(numFix))
        print('     Average fixation duration: ' + str(avgFix) + 'ms')

    return Fixations


def saccade(x, y, v, time, events, printing):
    """Calculate Saccade measures

	arguments

	x		-	numpy array of x positions
	y		-	numpy array of y positions
	v       -   numpy array of velocities
	time	-	numpy array of tracker timestamps in milliseconds
    events      -   numpy array of of detected gaze events

	returns
			Saccades	-	list of lists, each containing [starttime, endtime, duration, startx, starty, endx, endy,  amplitude, meanvel, maxvel])]
	"""

    # empty list to contain data
    Saccades = []

    # check where the missing samples are
    idx = numpy.array(events == 'SACCADE', dtype=int)

    # check where the starts and ends are (+1 to counteract shift to left)
    diff = numpy.diff(idx)
    starts = numpy.where(diff == 1)[0] + 1
    ends = numpy.where(diff == -1)[0] + 1

    # delete detected starts and ends from before and after recording
    if idx[-0] == 1:
        starts = starts[0:-1]
    if idx[0] == 1:
        ends = ends[1::]
    if len(starts) > len(ends):
        ends = np.append(ends, len(idx) - 1)

    # compile saccade starts and ends
    for i in range(len(starts)):
        # get starting index
        s = starts[i]
        # get ending index
        if i < len(ends):
            e = ends[i]
        elif len(ends) > 0:
            e = ends[-1]
        else:
            e = -1

        # writing data
        duration = time[e] - time[s]
        amplitude = ((x[s] - x[e]) ** 2 + (y[s] - y[e]) ** 2) ** 0.5
        meanvel = sum(v[s:e]) / len(v[s:e])
        maxvel = max(v[s:e])

        Saccades.append([time[s], time[e], duration, x[s], y[s], x[e], y[e], amplitude, meanvel, maxvel])

    Saccades = numpy.array(Saccades)
    if Saccades.any() and printing:
        numSac = len(Saccades)
        avgSacT = 1000 * sum(Saccades[:, 2]) / numSac
        avgSacA = sum(Saccades[:, 7]) / numSac
        avgSacV = sum(Saccades[:, 8]) / numSac
        avgSacMV = sum(Saccades[:, 9]) / numSac
        print('Number of saccades: ' + str(numSac))
        print('     Average saccades duration: ' + str(avgSacT) + ' ms')
        print('     Average saccades Amplitude: ' + str(avgSacA) + ' deg')
        print('     Average saccades velocity: ' + str(avgSacV) + ' deg/s')
        print('     Average max saccades velocity: ' + str(avgSacMV) + ' deg/s')

    return Saccades


def persuit(x, y, v, time, events, printing):
    """Calculates Persuit measures
	arguments

	x		-	numpy array of x positions
	y		-	numpy array of y positions
	v       -   numpy array of velocities
	time	-	numpy array of tracker timestamps in milliseconds
    events      -   numpy array of of detected gaze events

	returns
				Persuits	-	list of lists, each containing [starttime, endtime, duration, startx, starty, endx, endy,  amplitude, meanvel, maxvel])]
	"""
    # empty list to contain data
    Persuits = []

    # check where the missing samples are
    idx = numpy.array(events == 'SP', dtype=int)

    # check where the starts and ends are (+1 to counteract shift to left)
    diff = numpy.diff(idx)
    starts = numpy.where(diff == 1)[0] + 1
    ends = numpy.where(diff == -1)[0] + 1

    # delete detected starts and ends from before and after recording
    if idx[-0] == 1:
        starts = starts[0:-1]
    if idx[0] == 1:
        ends = ends[1::]
    if len(starts) > len(ends):
        ends = np.append(ends, len(idx) - 1)

    # compile persuit starts and ends
    for i in range(len(starts)):
        # get starting index
        s = starts[i]
        # get ending index
        if i < len(ends):
            e = ends[i]
        elif len(ends) > 0:
            e = ends[-1]
        else:
            e = -1

        # writing data
        duration = time[e] - time[s]
        amplitude = ((x[s] - x[e]) ** 2 + (y[s] - y[e]) ** 2) ** 0.5
        meanvel = sum(v[s:e]) / len(v[s:e])
        maxvel = max(v[s:e])

        Persuits.append([time[s], time[e], duration, x[s], y[s], x[e], y[e], amplitude, meanvel, maxvel])

    Persuits = numpy.array(Persuits)
    if Persuits.any() and printing:
        numSP = len(Persuits)
        avgSPT = 1000 * sum(Persuits[:, 2]) / numSP
        avgSPA = sum(Persuits[:, 7]) / numSP
        avgSPV = sum(Persuits[:, 8]) / numSP
        avgSPMV = sum(Persuits[:, 9]) / numSP
        print('Number of Smooth Persuits: ' + str(numSP))
        print('     Average persuit duration: ' + str(avgSPT) + 'ms')
        print('     Average persuit Amplitude: ' + str(avgSPA) + ' deg')
        print('     Average persuit velocity: ' + str(avgSPV) + ' deg/s')
        print('     Average max persuit velocity: ' + str(avgSPMV) + ' deg/s')

    return Persuits


def blink(time, events, printing):
    """Calculates Blink measures
	arguments
                time		-	numpy array of EyeTribe timestamps
                events      -   numpy array of of detected gaze events

	returns
		        Blinks	-	list of lists, each containing [starttime, endtime, duration]
	"""
    # empty list to contain data
    Blinks = []

    # check where the missing samples are
    idx = numpy.array(events == 'BLINK', dtype=int)

    # check where the starts and ends are (+1 to counteract shift to left)
    diff = numpy.diff(idx)
    starts = numpy.where(diff == 1)[0] + 1
    ends = numpy.where(diff == -1)[0] + 1

    # delete detected starts and ends from before and after recording
    if idx[-0] == 1:
        starts = starts[0:-1]
    if idx[0] == 1:
        ends = ends[1::]
    if len(starts) > len(ends):
        ends = np.append(ends, len(idx) - 1)

    # compile blink starts and ends
    for i in range(len(starts)):
        # get starting index
        s = starts[i]
        # get ending index
        if i < len(ends):
            e = ends[i]
        elif len(ends) > 0:
            e = ends[-1]
        else:
            e = -1

        # add ending time
        Blinks.append([time[s], time[e], time[e] - time[s]])

    Blinks = numpy.array(Blinks)
    if Blinks.any() and printing:
        numBlk = len(Blinks)
        avgBlk = 1000 * sum(Blinks[:, 2]) / numBlk
        print('Number of blinks: ' + str(numBlk))
        print('     Average blink duration: ' + str(avgBlk) + 'ms')

    return Blinks
