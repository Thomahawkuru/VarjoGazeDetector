import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import rayleigh
from scipy.stats import norm

"""
Functions for helping with plotting of various figures and data
"""

def detection(x, y, t, v, fixations, saccades, persuits, blinks, trail, axs):
    axs1 = axs[trail - 1]
    axs1.set_title('Trail ' + str(trail))
    axs1.set_xlabel('Time [s]')

    axs1.plot(t, v, 'silver', label="Velocity")
    axs1.set_ylabel('Velocity [deg/s]')
    axs1.set_ylim([-1000, 1000])

    axs2 = axs1.twinx()
    axs2.plot(t, x, 'tab:orange', label="Horizontal")
    axs2.plot(t, y, 'tab:green', label="Vertical")
    axs2.set_ylabel('Angel [deg]')
    axs2.set_ylim([-22.5, 22.5])

    for i in range(len(fixations)):
        axs1.axvspan(fixations[i, 0], fixations[i, 1], color='g', alpha=.1, label =  "_"*i + "Fixations")
    for i in range(len(saccades)):
        axs1.axvspan(saccades[i, 0], saccades[i, 1], color='r', alpha=.1, label =  "_"*i + "Saccades")
    for i in range(len(persuits)):
        axs1.axvspan(persuits[i, 0], persuits[i, 1], color='y', alpha=.1, label =  "_"*i + "Persuits")
    for i in range(len(blinks)):
        axs1.axvspan(blinks[i, 0], blinks[i, 1], color='b', alpha=.1, label =  "_"*i + "Blinks")

    axs1.legend(loc='upper left')
    axs2.legend(loc='upper right')

def calculation(fixations, saccades, persuits, blinks, trail, participant):
    plt.figure(trail + 1, figsize=[25.60, 14.40])
    plt.subplot(4, 4, 1)
    histogramreighley(fixations[:, 2])
    plt.title("Fixation duration")
    plt.xlabel('Time [s]')

    plt.subplot(4, 4, 5)
    histogramreighley(saccades[:, 2])
    plt.title("Saccade duration")
    plt.xlabel('Time [s]')
    plt.subplot(4, 4, 6)
    histogramreighley(saccades[:, 7])
    plt.title("Saccade amplitude")
    plt.xlabel('Amplitude [deg]')
    plt.subplot(4, 4, 7)
    histogramreighley(saccades[:, 8])
    plt.title("Saccade mean velocity")
    plt.xlabel('Velocity [deg/s]')
    plt.subplot(4, 4, 8)
    histogramreighley(saccades[:, 9])
    plt.title("Saccade max velocity")
    plt.xlabel('Velocity [deg/s]')

    plt.subplot(4, 4, 9)
    histogramreighley(persuits[:, 2])
    plt.title("Persuit duration")
    plt.xlabel('Time [s]')
    plt.subplot(4, 4, 10)
    histogramreighley(persuits[:, 7])
    plt.title("Persuit amplitude")
    plt.xlabel('Amplitude [deg]')
    plt.subplot(4, 4, 11)
    plt.xlabel('Amplitude [deg]')
    histogramreighley(persuits[:, 8])
    plt.title("Persuit mean velocity")
    plt.xlabel('Velocity [deg/s]')
    plt.subplot(4, 4, 12)
    histogramreighley(persuits[:, 9])
    plt.title("Persuit max velocity")
    plt.xlabel('Velocity [deg/s]')

    plt.subplot(4, 4, 13)
    histogramreighley(blinks[:, 2])
    plt.title("Blink duration")
    plt.xlabel('Time [s]')

    plt.tight_layout()


def histogramreighley(data):
    N = len(data)
    scale = data.mean() / np.sqrt(np.pi / 2)
    V_norm_hist = scale * np.sqrt(-2 * np.log(np.random.uniform(0, 1, N)))

    num_bins = 30
    _binvalues, bins, _patches = plt.hist(V_norm_hist, bins=num_bins, density=False, rwidth=1, ec='white',
                                          label='Histogram data')
    x = np.linspace(bins[0], bins[-1], 100)
    binwidth = (bins[-1] - bins[0]) / num_bins

    scale = V_norm_hist.mean() / np.sqrt(np.pi / 2)

    plt.plot(x, rayleigh(loc=0, scale=scale).pdf(x) * len(V_norm_hist) * binwidth, lw=5, alpha=0.6,
             label=f'Rayleigh pdf (s={scale:.3f})')
    plt.axvline(data.mean(), color='red', lw=3, alpha=0.6, label='Mean = ' + str(data.mean()))
    plt.ylabel('samples [n]')
    plt.grid(True)
    plt.legend()


def histogramfit(data):
    # best fit of data
    (mu, sigma) = norm.fit(data)

    # the histogram of the data
    n, bins, patches = plt.hist(data, len(data), alpha=0.75)

    # add a 'best fit' line
    y = norm.pdf(bins, mu, sigma)
    l = plt.plot(bins, y, 'r--', linewidth=2)

    # plot
    plt.ylabel('samples [n]')
    plt.title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=%.3f,\ \sigma=%.3f$' % (mu, sigma))
    plt.grid(True)
