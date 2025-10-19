"""Alignment utilities

This module contains functions to help align images.
"""
import numpy as np
import astroalign
from astropy.io import fits
from glob import glob
import os
from skimage.util import img_as_float64
from ..utils.context_managers import indir


def align_with(image, ref_matrix, ref_file, max_control_points=50, min_area=5):
    """
    Given a FITS file it will open the file and align to the reference image
    matrix and rewrite the file.
    It uses the astroalign package that align stellar astronomical images with
    an 3 point matching (triangle). It need above about 10 stellar sources in
    an image (based on the tests).

    # This function takes the matrix directly (instead of path to file)
    because of performance. This function in meant to be used within a loop,
    with this the ref_matrix needs to be loaded just once.

    Parameters
    ----------
        image : str
            Path to image to align with the reference.
        ref_matrix : Numpy 2D array
            Reference image.
        ref_name : str
            Name of reference FITS file.

    Returns
    -------
        None.

    File transformation:
        Re-write FITS file pointed at image variable with updated header.
    """
    # Loading

    data = fits.getdata(image)
    data = img_as_float64(data)  # Converting to float to avoid scikitimage bug
                                 # Issue #4525

    header = fits.getheader(image)
    new_image = "a_" + image

    # Aligning

    aligned_image, _ = astroalign.register(
            data,
            ref_matrix, 
            max_control_points=max_control_points,
            min_area=min_area
            )

    # Re-write file and update header

    header["ALIGNED-TO"] = ref_file


    fits.writeto(new_image, aligned_image.astype(np.float32), header)
    os.remove(image)


def align_all_images(
        images_folder,
        ref_file=None,
        max_control_points=50,
        min_area=5
        ):
    """
    Align all FITS stellar images to reference file. If reference file is set
    to None it uses the first image in the folder.

    # Wraps align_with function.

    Parameters
    ----------
        images_folder : str
            Path to folder with images to align.
        ref_file : str
            Path to FITS with reference field. Default is None, so it takes
            the first file of the folder.

    Returns
    -------
        None.

    File transformation
    -------------------
        Re-write FITS files with aligned version.
    """

    with indir(images_folder):
        images = glob("*.fits")
        images.sort()

        if ref_file == None:
            ref_file = images[0]

        ref_image = img_as_float64(fits.getdata(ref_file))
        N = len(images)


        print(f"Aligning {N} images with file {ref_file} in folder {images_folder}.\n")

        for i, im in enumerate(images, start=1):
            if "a_" not in im:
                # try:
                print(f"Aligning: {im} ({i} of {N}).")
                align_with(im, ref_image, ref_file, max_control_points=max_control_points, min_area=min_area)
                # except:
                #     print(f"Some problem has happened with the alignment of image {im}")
                #     continue

        print(f"\n Finished alignment of {images_folder} images.")
