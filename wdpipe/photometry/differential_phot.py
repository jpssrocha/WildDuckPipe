"""
Functions to perform differential photometry over a light curve catalog
generated with the aperture_photometry module.
"""
import numpy as np
import matplotlib.pyplot as plt


def convert_to_flux(x):
    """Covert value (x) from magnitude to flux"""
    return 10**(-x/2.512)


def convert_to_magnitude(x):
    """Covert value (x) from flux to magnitude"""
    return -2.512*np.log10(x)


def calc_ref_magnitude(time_series, n=10):
    """
    From time series table (generated with assemble_lightcurve) get the `n`
    stars with the lowest std along the time series to generate reference
    magnitudes for each frame.

    OBS: This function is supposed to be used with the lightcurve of a star
         clusters, hence the n. For field variables with a poor field.

    Parameters
    -----------
        time_series : np.ndarray
            Light curves generated using the assemble_lightcurve function.
            generated using the assemble_lightcurve function.

        n : int
            Size of the sample to use as reference.

    Returns
    -------
        ref_magnitudes : np.ndarray
            1d array with reference magnitude for each point of the lightcurve.

        ref_stars : np.ndarray
            2d array with the data from the reference sample.
    """

    if n > time_series.shape[0] - 1:
        print("Number of stars greater than the number of stars on the field minus 1 !\n")
        print("So no stars left for the photometry. Review what you're doing!")
        return None

    ts = time_series[:, 3::2]

    stdev = np.nanstd(ts, axis=1, ddof=1)
    ordered_stdev = np.sort(stdev)
    ref_std = ordered_stdev[:n]  # n'th smaller std's
    ref_mask = np.isin(stdev, ref_std)

    ref_stars = time_series[ref_mask]

    ref_magnitudes = np.nanmean(ts[ref_mask], axis=0)

    return ref_magnitudes, ref_stars


def differential_photometry(time_series, n=100, out=None, viz=False):
    """
    Performs a simple differential photometry and produces the dispersion chart.

    Parameters
    -----------
        time_series : np.ndarray
            Light curve generated using the assemble_lightcurve function.

        n : int
            Size of the sample to use as reference.

        out : str or None, default=None
            Name to save chart, if None it doesn't save.

        viz : bool, default=False
            If True show the chart.

    Returns
    -------
        ref_magnitudes : np.ndarray
            1d array with reference magnitude for each point of the lightcurve.

        ref_stars : np.ndarray
            2d array with the data from the reference sample.

        diff_ts : np.ndarray
            2d array with the differential light curves.
    """

    if n > time_series.shape[0] - 1:
        print("Number of stars greater than the number of stars on the field minus 1 !\n")
        print("So no stars left for the photometry. Review what you're doing!")
        return None

    ts = time_series[:, 3::2]
    pos = time_series[:, :3]

    ref_mags, ref_stars = calc_ref_magnitude(time_series, n=n)

    diff_ts = ts - ref_mags

    means = np.nanmean(diff_ts, axis=1)
    stds = np.nanstd(diff_ts, axis=1, ddof=1)

    fig, ax = plt.subplots()

    ax.scatter(means, stds, s=20, alpha=.5)
    ax.set_xlim(-2, 6)
    ax.set_ylim(0, .2)
    ax.set_title("Magnitude diferencial média por desvio padrão (banda V)")
    ax.set_ylabel("Desvio Padrão da magnitude")
    ax.set_xlabel("Magnitude Média ")
    ax.yaxis.grid()
    fig.tight_layout()

    if out != None:
        fig.savefig(f"{out}.png")

    if viz:
        fig.show()

    diff_ts = np.hstack([pos, diff_ts])

    return ref_mags, ref_stars, diff_ts

def targeted_differential_photometry():
    pass
