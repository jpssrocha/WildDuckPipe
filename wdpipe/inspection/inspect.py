#!/usr/bin/env python
"""

Utilities to inspect images. It works also as a script for getting a inspection
via the command line.

Usage
-----

    $python inspect <folder> <refs> <out>

Where:
        <folder>: is where the images are (they should be aligned)
        <refs>: is a file with the coordinates of patches of sky and of stars
        <out>: is the name of the file to be created

OBS:
    refs is a dataset with the following columns: kind, x, y. Where kind is if
    it is a star or sky (categorical "star" or "sky") and x,y are the central
    pixel coordinate (integers with pixel positions)
"""
import os
from glob import glob


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astropy.modeling.models import Moffat1D
from astropy.modeling.fitting import LevMarLSQFitter
from astropy.io import fits
from photutils.centroids import centroid_1dg


from wdpipe.utils.context_managers import indir

def get_stats(img_matrix, take=["min", "max", "mean", "median", "std"]):
    """
    Given image matrice return basic stats of pixel count. Can do so for any
    array.

    Args:
        img_matrix -- Numpy array containing the image.
        take -- List containing statistics to take, default is all stats.

    Return:
        img_stats -- List with statistics of image in the order of the take
        list.
    """

    stats = {"min": np.min,
             "max": np.max,
             "mean": np.mean,
             "median": np.median,
             "std": np.std}

    img_stats = {}
    for stat in take:
        img_stats[stat] = np.apply_along_axis(stats[stat],
                                              0,  # Axis
                                              np.ravel(img_matrix)).item()

    return img_stats


def get_square(img_matrix, x0, y0, delta=8):
    """
    Get a square matrix around element in position x0, y0 of size 2*delta

    Args:
        img_matrix -- 2D numpy array of image.
        x0, y0 -- Integers telling coordinates of desired pixel.
        delta -- Integer telling quantity of elements to take on each side.

    Return:
        Numpy 2D square array with values of elements within selection window.
    """

    xa, ya = x0-delta, y0-delta
    xb, yb = x0+delta, y0+delta

    return img_matrix[ya:yb, xa:xb]


def get_sky(img_matrix, xs, ys, delta = 8):
    """
    Uses the get_square to extract patches pointed as xy pairs and calculate
    the sigma.  Meant to estimate sky sigma.

    Args:
        img_matrix -- 2D numpy array of image.
        xs -- List of x positions
        ys -- List of y positions
        delta -- Integer for window size

    Return:
        Dict of Floats with median standard deviation of all squares

    """
    if len(xs) != len(ys):
        print("Warning !!! : x and y length doesn't match!! Exiting function.")
        return None

    squares = []
    for i, j in zip(xs, ys):
        squares.append(get_square(img_matrix, i, j, delta))

    squares = np.array(squares)
    stds = squares.std(axis=0)
    sky = np.median(squares, axis=0)

    return {"bkg_sky": np.median(sky), "sky_sigma": np.median(stds)}


def mfwhm(star_matrix, sky=0, delta=8, plot=False):
    """
    Get star center and use it to calulate FWHM using a Moffat function fit.

    Args:
        star_matrix -- 2D numpy array of image of a star.
        sky -- Float giving sky background counts.
        delta -- Integer for window size.

    Return:
        Float giving FWHM.
    """
    star_2 = np.copy(star_matrix)

    if sky == 0:
        sky = star_2.min()

    star_2 -= sky

    tx, ty = centroid_1dg(star_2)

    indices = np.ogrid[[slice(0, i) for i in star_2.shape]]
    dist = np.sqrt((ty - indices[0])**2 + (tx - indices[1])**2)

    x = dist.ravel()
    y = star_2.ravel()

    model_init = Moffat1D(amplitude=star_2.max(), x_0=0)
    fitter = LevMarLSQFitter()

    model_fit = fitter(model_init, x, y)

    if plot:
        xx = np.linspace(-1, delta*2, 100)
        plt.plot(xx, model_fit(xx), c="k")
        plt.scatter(dist.ravel(), y, alpha=0.5, s=10)
        plt.show()
        plt.imshow(star_2)
        plt.show()
        print(model_fit.fwhm)

    return model_fit.fwhm


def get_mfwhm(img_matrix, xs, ys, sky=0, delta=8):
    """
    Uses the get_square to extract patches with stars pointed using xy pairs.
    Then extract mfwhm from each

    Args:
        img_matrix -- 2D numpy array of image.
        xs -- List of x positions
        ys -- List of y positions
        delta -- Integer for window size

    Return:
        Float giving fwhm average of all points
    """
    if len(xs) != len(ys):
        print("Warning !!! : x and y length doesn't match!! Exiting function.")
        return None

    squares = []
    for i, j in zip(xs, ys):
        squares.append(get_square(img_matrix, i, j, delta))

    estimatives = []
    for star in squares:
        estimatives.append(mfwhm(star, sky, delta))

    return np.mean(estimatives)


def get_image_parameters(image, ref_stars_x, ref_stars_y, ref_sky_x, ref_sky_y):
    """
    Given an image, return the parameters for inspection (basic stats +
    background sky + sky sigma) in a dictionary.

    Args:
        image -- String with path to the image to analise.
        ref_stars_x -- List of Ints with x coordinate to star center pixel.
        ref_stars_y -- List of Ints with x coordinate to star center pixel.
        ref_sky_x -- List of Ints with x coordinate to sky pixel.
        ref_sky_y -- List of Ints with x coordinate to sky pixel.

    Return:
        Dictionary containing image information, basic stats and basic
        parameters.
    """

    data = fits.getdata(image)
    header = fits.getheader(image)

    info = {"file": image.split("/")[-1],
            "jd": header["JD"],
            "airmass": header["AIRMASS"]}

    info.update(get_stats(data))
    info.update(get_sky(data, ref_sky_x, ref_sky_y))
    info["FWHM"] = get_mfwhm(data, ref_stars_x, ref_stars_y, sky=info["bkg_sky"])
    return info


def get_parameters_all(folder, ref_stars_x, ref_stars_y, ref_sky_x, ref_sky_y):
    """
    Return and write a Data Frame with parameters extracted with
    get_image_parameters for all images in a folder.

    Args:
        folder -- String with path to folder
        ref_stars_x -- List of Ints with x coordinate to star center pixel.
        ref_stars_y -- List of Ints with x coordinate to star center pixel.
        ref_sky_x -- List of Ints with x coordinate to sky pixel.
        ref_sky_y -- List of Ints with x coordinate to sky pixel.

    Return:
        Pandas Dataframe containing information on all fits files of the folder
    """
    with indir(folder):

        files = glob("*.fits")
        files.sort()

        N = len(files)

        dicts = []
        for i, image in enumerate(files, start=1):
            print(f"Getting parameters for file: {image} ({i} of {N})")
            dicts.append(get_image_parameters(image, ref_stars_x, ref_stars_y, ref_sky_x, ref_sky_y))

        df = pd.DataFrame(dicts)

    print("\nFinished getting parameters!")

    # Casting to float since the information on the header comes as string
    df.jd = df.jd.astype(np.float64)
    df.airmass = df.airmass.astype(np.float64)

    # To ensure it is in chronological order
    df.sort_values(by="jd", inplace=True)

    return df


def inspect(image_folder, ref_file, out_name):
    """
    Given a folder with aligned images, a file containing the position for sky
    and star patches and a output name, create a file containing a dataset
    with parameters extracted from the images.

    OBS: Basically parse the ref_file and pass to get_parameters_all.

    Args:
        image_folder -- str with path to folder
        ref_file -- str with path to file
        out_name -- str with name to give to the exit file

    Returns:
        parameters -- pd.DataFrame with the parameters extracted from the
                      images.

    File transformations:
        Write the parameters dataframe in CSV with the name on out_name.

    """

    ref_df = pd.read_csv(ref_file)

    stars = ref_df.loc[ref_df.kind == "star"]
    sky = ref_df.loc[ref_df.kind == "sky"]

    parameters = get_parameters_all(image_folder, stars.x, stars.y, sky.x, sky.y)

    parameters.to_csv(out_name, index=False)

    return parameters


if __name__ == "__main__":

    import sys

    folder = sys.argv[1]
    positions = sys.argv[2]
    out_file = sys.argv[3]

    parameters = inspect(folder, positions, out_file)
