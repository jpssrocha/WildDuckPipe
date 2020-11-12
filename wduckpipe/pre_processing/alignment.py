"""Alignment utilities

This module contains functions to help align images.
"""
import numpy as np
import astroalign
from astropy.io import fits
from glob import glob
import os
from scikitimage.util import img_as_float

def align_with(image, ref_matrix, ref_file):
    """
    Given a FITS file it will open the file and align to the reference image
    matrix and rewrite the file.
    It uses the astroalign package that align stellar astronomical images with
    an 3 point matching (triangle). It need above about 10 stellar sources in
    an image (based on the tests).

    # This function takes the matrix directly (instead of path to file)
    because of performance. This function in meant to be used within a loop,
    with this the ref_matrix needs to be loaded just once.

    Args:
        image -- String containing path to image to align with the reference.
        ref_matrix -- Numpy 2D array containing reference image.
        ref_name -- String with name of reference FITS file.

    Return:
        None.

    File transformation:
        Re-write FITS file pointed at image variable with updated header.
    """
    # Loading

    data = fits.getdata(image)
    data = img_as_float(data) # Converting to float to avoid scikitimage bug
                              # Issue #4525

    header = fits.getheader(image)
    new_image = "a" + image

    # Aligning

    aligned_image = astroalign.register(data, ref_matrix)

    # Re-write file and update header

    header["ALIGNED-TO"] = ref_file

    fits.writeto(new_image, aligned_image, header)
    os.remove(image)

def align_all_images(images_folder, ref_file=None):
    """
    Align all FITS stellar images to reference file. If reference file is set
    to None it uses the first image in the folder.

    # Wraps align_with function.

    Args:
        images_folder -- String with path to folder with images to align.
        ref_file -- String with path to FITS with reference field. Default is
                    None, so it takes the first file of the folder.

    Return:
        None.

    File transformation:
        Re-write FITS files with aligned version.
    """
    os.chdir(images_folder)
    images = glob("*.fits")
    images.sort()

    if ref_file == None:
        ref_file = images[0]

    ref_image = img_as_float(fits.getdata(ref_file))
    N = len(images)


    print(f"Aligning {N} images with file {ref_file} in folder {images_folder}.\n")

    for i, im in enumerate(images, start=1):
        print(f"Aligning: {im} ({i} of {N}).")
        align_with(im, ref_image, ref_file)

    print(f"\n Finished alignment of {images_folder} images.")

    os.chdir("../")
