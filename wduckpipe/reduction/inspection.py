"""
Module containing functions to the inspection algorithm
"""
import astroalign as aa
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from matplotlib.colors import LogNorm
import glob, os, gc

def display(image_matrice):
    "Given an image matrice as a np 2d array displays it with plt.imshow"
    plt.imshow(image_matrice,
                norm=LogNorm(vmin=image.min()+100, vmax=image.max()-100),
                cmap="gray")

def norm_by_average(array):
    "Takes numpy array and gives it back normalized"
    return array/np.average(array)

def extract_block(cube, x0, y0, delta=5):
    """"
    Given an image data cube, as a numpy 3d array, returns a block of the
    array along the 0 axis around the target point (x0,y0) with an 2*delta
    side lenght in pixels
    """
    xa, ya = x0-delta, y0-delta
    xb, yb = x0+delta, y0+delta
    return cube[:, ya:yb, xa:xb]

def sigma_block(cube, x, y, delta=5):
    """
    Given lists of x and y coordinates of the central pixels, from sky
    areas, gives back the std within a (2*delta)**2 pix**2 area.
    """
    if len(x) != len(y):
        print("x and y lenght doesn't match!! Exiting function.")
        return None

    blocks = []

    for i,j in zip(x,y):
        block = extract_block(cube, i, j)
        block = block.reshape(block.shape[0],
                              block.shape[1]*block.shape[2])
        blocks.append(block)

    sigma = [np.std(block, axis=1) for block in blocks]

    return np.average(np.array(sigma), axis=0)
