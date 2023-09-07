"""
Functions to perform aperture photometry over a folder of FITS files.
"""
from glob import glob

import numpy as np
import pandas as pd
from astropy.io import fits
from photutils import DAOStarFinder
from photutils import CircularAnnulus, CircularAperture

from wdpipe.utils.context_managers import indir
import wfc3_photometry.photometry_tools.photometry_with_errors as phot



def get_catalog(ref_image, pars, nsigma=5):
    """
    Detect sources in image and create catalog of id, x_center and y_center of
    stars.

    Args:
        ref_image -- String with path to reference image.
        pars -- Pandas Series with image parameters.
        nsigma -- Integer to multiply the sky sigma adding to the background
                  for threshold.

    Return:
        positions -- 2D numpy array with catalog (Columns: 0 - ID; 1 - Xcenter; 2 - Ycenter)
        sources -- Table containing the source properties
    """

    matrix = fits.getdata(ref_image)

    finder = DAOStarFinder(fwhm=pars["FWHM"],
                           threshold=pars["bkg_sky"] + nsigma*pars["sky_sigma"])

    sources = finder(matrix)

    positions = np.transpose((
        sources["id"],
        sources["xcentroid"],
        sources["ycentroid"]))

    return positions, sources


def get_photometry(
        image,
        catalog,
        pars,
        aperture_factors={"r": 2.0, "r_in": 2.5, "r_out": 3.5},
        zero_point=25,
        first=False):
    """
    Use catalog to generate photometry table.

    Args:
        ref_image -- String with path to reference image.
        catalog -- 2D numpy array with table created with get_catalog.
        pars -- Pandas Series with image parameters.
        aperture_factors -- Dict with factors to scale apertures in units of FWHM.
        zero_point -- Integer used as default zero point for the photometry.
        first -- Boolean to indicate if it is the first of a time series.
                 If True return ID, X and Y positions on return in addition
                 to magnitude and error.

    Return:
        Numpy 2D array with table of photometry.
    """

    #  Load data
    matrix = fits.getdata(image)
    header = fits.getheader(image)
    fwhm = pars["FWHM"]
    positions = catalog[:, 1:]
    indexes = catalog[:, 0][:, None]

    #  Create apertures
    apertures = CircularAperture(positions,
                                 r=aperture_factors["r"]*fwhm)
    sky_annulus = CircularAnnulus(positions,
                                  r_in=aperture_factors["r_in"]*fwhm,
                                  r_out=aperture_factors["r_out"]*fwhm)

    matrix[matrix <= 0] = pars["sky_sigma"]

    photometry = phot.iraf_style_photometry(apertures,
                                            sky_annulus,
                                            matrix,
                                            epadu=float(header["GAIN"]))

    photometry["mag"] = zero_point + photometry["mag"]

    if first:
        #  ID, Xcenter, Ycenter, MAG, MERR
        return np.hstack([indexes,
                          (photometry
                           .to_pandas()[["X", "Y", "mag", "mag_error"]]
                           .to_numpy())])

    # Xcenter, Ycenter
    return photometry.to_pandas()[["mag", "mag_error"]].to_numpy()


def assemble_lightcurve(
        image_folder,
        catalog,
        pars_ds,
        aperture_factors={"r": 2, "r_in": 2.5, "r_out": 3.5}):
    """
    Apply get photometry iteravively in all images of a folder to create a
    light curve table.

    Args:
        image_folder -- String with path to folder with the images.
        catalog -- 2D numpy array with table created with get_catalog.
        pars_ds -- String with path to parameters file.
        aperture_factors -- Dict with factors to scale apertures in units of
                            FWHM.

    Return:
        light_curve -- 2D numpy array with table of light curve.

    """

    pars = pd.read_csv(pars_ds, index_col="file")

    with indir(image_folder):

        images = glob("*.fits")
        images.sort()


        print(f"Starting to assemble time series table of images on {image_folder}")


        light_curve = get_photometry(images[0],
                                     catalog,
                                     pars.loc[images[0]],
                                     aperture_factors=aperture_factors,
                                     first=True)

        images = images[1:]
        N = len(images)

        for i, im in enumerate(images, start=1):
            print(f"Doing photometry of {im} ... ({i} of {N})")
            light_curve = np.hstack([light_curve,
                                     get_photometry(im,
                                                    catalog,
                                                    pars.loc[im],
                                                    aperture_factors=aperture_factors)])

        print("Finished Photometry.")

    return light_curve
