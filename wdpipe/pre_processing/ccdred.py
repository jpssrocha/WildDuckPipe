"""
Module containing CCD image reduction routines:
    - Overscan correction
    - Master generation (bias and flat)
    - Aplication of calibrations (ccdproc)

"""
import pandas as pd
import .nightlog
from pathlib import Path
import os
from astropy.io import fits
import numpy as np
from astropy.nddata import CCDData
import ccdproc


def _check_image_extensions(hdul):
    """
    Given a HDUList object, verify with extensions contains images. And return
    it's index.

    Parameters
    ----------
        hdul : astropy.io.fits.HDUList
            HDUList object to check.

    Returns
    -------
        index_list : list
            Indexes of image extensions.
    """
    image_indices = np.arange(len(hdus))
    selection = [hdu.size > 0 for hdu in hdus]
    index_list = image_indices[selection]

    return index_list


def correct_overscan(file_path):
    """
    Given a list of FITS filenames, does overscan correction over all image
    extensions.
    
    Arguments
    ---------
        files_path : str
            Path to the file to process.
            
    File transformations
    --------------------
    
        Re-write FITS file, with overscan correction and updated header.
    
    
    Returns
    -------
        None
    """

    hdul = fits.open(file_path)
    image_indices = _check_image_extensions(hdul)

    #  Loop over extensions
    for i in image_indices:
        #  Aborting if the keyword 'BIASSEC' isn't defined
        if not ('BIASSEC' in hdul[i].header): 
            print( f"""Skipping overscan correction on: {file:1s}[{i:1.0f}]
                    - BIASSEC keyword not found"""
                )
            continue

        img = CCDData(
                data=hdul[i].data,
                header=hdul[i].header,
                unit="adu"
                )

        img_osub = (
                ccdproc.subtract_overscan(
                    img, 
                    fits_section=img.header['BIASSEC'],
                    model=None,
                    median=True,
                    add_keyword={'overscan': True, 'calstat': 'O'})
                )

        img_trim = (
                ccdproc.trim_image(
                    img_osub,
                    fits_section=img_osub.header['TRIMSEC'], 
                    add_keyword={'trimmed': True, 'calstat': 'OT'})
                )

        #  Updating header and overwriting processed image
        del img_trim.header['BIASSEC']
        del img_trim.header['TRIMSEC']

        fits.update(
                file_path,
                img_trim.data.astype(np.float32),
                header=img_trim.header,
                ext=i
                )

    hdul.close()



    def _center_inv_median(image_matrix):
    """
    Given an image return the inverse of the median from the central region
    of the image (1/4 of the image). To use whithin the make_mflat function.
    
    Arguments
    ---------
        image_matrix : 2D np.array
            matrix of the image.
            
    Returns
    -------
        inv_med : float
            Inverse of the central region median
    """
    
    #  Orientation
    y, x = image_matrix.shape
    y, x = int(y/2), int(x/2) # Center
    dy, dx = int(y/2), int(x/2) # Step
    
    #  Limits
    a, b = y - dy, y + dy
    c, d = x - dx, x + dy
    
    roi = image_matrix[a:b, c:d]
    
    inv_med = 1/np.median(roi)
    
    return inv_med
    
    
def make_mflat(file_list, mbias_path, out_path, filter, out_name="master_flat"):
    """
    Given a list of flat image files, combine then into master flat using
    sigma clipping algorithm, on the images after normalizing by the median. It
    is expected that the files are already pre-processed (overscan, trim, ...).
    
    Arguments
    ---------
    
        file_list : list of str
            Paths for the files.
            
        mbias_path : str
            Path to the master bias
            
        out_path : pathlib.Path 
            Location to put new image
            
        filter: str
            Name of filter (used to generate out filename)
        
        out_name : str
            Name of output file. (default is master_flat_<filter>)
            
    File transformations
    --------------------
    
        Re-write FITS files, with overscan correction and updated header.
    
    
    Returns
    -------
        out_pathname : str
            Path to the generated file.
    """
    
    out_pathname = out_path / (out_name + f"_{filter}.fits") 
    
    if out_pathname.exists():
        print(f"File: {str(out_pathname)} already exists.  Exiting the function.")
        return {filter : out_pathname}
    else:
        out_pathname = str(out_pathname)
    
    #  Checking first HDUList for the image extensions
    with fits.open(file_list[0]) as hdus
        image_indices = _check_image_extensions(hdus)

    #  Generating dummy file using the first image
    mflat = fits.open(file_list[0])
    mflat.writeto(out_pathname)
    
    #  Looping over extensions
    for i in image_indices:
        
        bias = CCDData.read(mbias_path, hdu=i, unit="adu")  #  Master bias
        #  Loading images of an extension
        ccd_list = [CCDData.read(image_file, hdu=i, unit="adu") for image_file in file_list]
        
        for image in ccd_list:
            image = ccdproc.subtract_bias(image, bias)

        #  Combining images
        comb = ccdproc.Combiner(ccd_list)
        comb.scaling = _center_inv_median # Scalling using custom function
        comb.sigma_clipping(low_thresh=3, high_thresh=3, func=np.ma.median)
        comb_image = comb.average_combine()

        #  Writing changes to the master bias file
        mflat[i].header.append(('NCOMBINE', len(ccd_list), '# images combined'))
        fits.update(out_pathname, comb_image.data, header=mflat[i].header, ext=i)
    
    mflat.close()
    print(f"Processed master flat on {filter} :  {out_pathname}")
    
    return {filter : out_pathname}


def ccdred(image_file, mbias_path, mflat_path):
    """
    Given a FITS file apply master calibration files.
    
    Arguments
    ---------
    
        image_file : str
            Path to the file to process
            
        mbias_path : str
            Path to the master bias
            
        mflat_path : str
            Path to the master flats
            
            
    File transformations
    --------------------
    
        Re-write FITS file, with overscan, bias and flat corrections and updated header.
    
    
    Returns
    -------
        None
    """
    
    hdul = fits.open(image_file)
    
    #  Checking HDU for the image extensions

    image_indices = _check_image_extensions(hdul)
    
    
    #  Looping over extensions
    for i in image_indices:
        
        if ('CCDPROC' in hdul[i].header): 
            print(f"Skipping image: {image_file:1s}[{i:1.0f}] - Already processed.")
            continue
        
        bias = CCDData.read(mbias_path, hdu=i, unit="adu")  
        flat = CCDData.read(mflat_path, hdu=i, unit="adu") 
        image = CCDData.read(image_file, hdu=i, unit="adu")
        
        image = ccdproc.subtract_bias(image, bias)
        image = ccdproc.flat_correct(image, flat, norm_value=1) 
        #  norm_value = 1 cause flat is already normalized

        #  Writing changes to the master bias file
        hdul[i].header.append(("CCDPROC", "True"))

        fits.update(
                image_file,
                image.data.astype(np.float32),
                header=hdul[i].header,
                ext=i
                )
        
        print(f"Processed file: {image_file:1s}[{i:1.0f}")
        
    hdul.close()
