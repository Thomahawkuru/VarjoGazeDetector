import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import rayleigh
from scipy.stats import norm

def detection(x, y, t, v, Fixations, Saccades, Persuits, Blinks, trail, axs):

    axs1 = axs[trail - 1]
    axs1.set_title('Trail ' + str(trail))
    axs1.set_xlabel('Time [s]')

    axs1.plot(t, v, 'silver')
    axs1.set_ylabel('Velocity [deg/s]')
    axs1.set_ylim([-1000, 1000])
    axs1.legend(["Velocity"])

    axs2 = axs1.twinx()
    axs2.plot(t, x, 'tab:orange')
    axs2.plot(t, y, 'tab:green')
    axs2.set_ylabel('Angel [deg]')
    axs2.set_ylim([-22.5, 22.5])
    axs2.legend(["Horizontal", "Vertical"])

    for i in range(len(Fixations)):
        axs1.axvspan(Fixations[i, 0], Fixations[i, 1], color='g', alpha=.1)
    for i in range(len(Saccades)):
        axs1.axvspan(Saccades[i, 0], Saccades[i, 1], color='r', alpha=.1)
    for i in range(len(Persuits)):
        axs1.axvspan(Persuits[i, 0], Persuits[i, 1], color='y', alpha=.1)
    for i in range(len(Blinks)):
        axs1.axvspan(Blinks[i, 0], Blinks[i, 1], color='b', alpha=.1)



def calculation(Fixations, Saccades, Persuits, Blinks, trail, participant):
    plt.figure(trail+1, figsize=[25.60, 14.40])
    plt.subplot(4, 4, 1)
    histogramreighley(Fixations[:, 2])
    plt.title("Fixation duration")
    plt.xlabel('Time [s]')

    plt.subplot(4, 4, 5)
    histogramreighley(Saccades[:, 2])
    plt.title("Saccade duration")
    plt.xlabel('Time [s]')
    plt.subplot(4, 4, 6)
    histogramreighley(Saccades[:, 7])
    plt.title("Saccade amplitude")
    plt.xlabel('Amplitude [deg]')
    plt.subplot(4, 4, 7)
    histogramreighley(Saccades[:, 8])
    plt.title("Saccade mean velocity")
    plt.xlabel('Velocity [deg/s]')
    plt.subplot(4, 4, 8)
    histogramreighley(Saccades[:, 9])
    plt.title("Saccade max velocity")
    plt.xlabel('Velocity [deg/s]')

    plt.subplot(4, 4, 9)
    histogramreighley(Persuits[:, 2])
    plt.title("Persuit duration")
    plt.xlabel('Time [s]')
    plt.subplot(4, 4, 10)
    histogramreighley(Persuits[:, 7])
    plt.title("Persuit amplitude")
    plt.xlabel('Amplitude [deg]')
    plt.subplot(4, 4, 11)
    plt.xlabel('Amplitude [deg]')
    histogramreighley(Persuits[:, 8])
    plt.title("Persuit mean velocity")
    plt.xlabel('Velocity [deg/s]')
    plt.subplot(4, 4, 12)
    histogramreighley(Persuits[:, 9])
    plt.title("Persuit max velocity")
    plt.xlabel('Velocity [deg/s]')

    plt.subplot(4, 4, 13)
    histogramreighley(Blinks[:, 2])
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
