"""
Program: Inspect.py
Description: Program to help inspecting the quality of the images
Version: ALPHA
Last change: 2019-08-09
"""
import module as m
import astroalign as aa
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from matplotlib.colors import LogNorm
import glob, os, gc

# MAIN

if __name__ == "__main__":

    files = glob.glob("r_*.fits")
    files.sort()

    reference_frame = "r_OI2018B-011_2018-10-21_0405.fits"

    images = {}
    headers = {}

    print("Carregando arquivos ...")

    for f in files:
        print(f)
        images[f] = fits.getdata(f)
        headers[f] = fits.getheader(f)

    total = len(images)
     

    print("Alinhando imagens ao frame de referência: ", reference_frame)

    for i,f in enumerate(files):
        print("Alinhando : %s (%i de %i)" % (f,i,total) ) 
        images[f],x = aa.register(images[f], images[reference_frame])

    data_cube = np.stack([images[f] for f in files], axis=0)

    # Usar reshape no cubo de dados para extrair estatísticas básicas

    data_plane = data_cube.reshape(data_cube.shape[0], data_cube.shape[1], data_cube.shape[2], )


    del images
    gc.collect()

