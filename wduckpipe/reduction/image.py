"""
Library containing functions related to the reduction of astronomical images.
Optimized to use with the standard adopted on mission OI2018B-011 from OPD/LNA
"""
import matplotlib.pyplot as plt
import numpy as np
import os
from glob import glob
from astropy.io import fits
from datetime import datetime as dt

# File movement functions


def move_files(files, destination):
    """
    Move list of files to specified destination.

    Args:
        files -- List object containing strings with the address of files.
        destination -- String containing destination folder.

    Return:
        None.
    """
    quantity = len(files)
    print("Moving", quantity, "files... \n")

    i = 1
    for file in files:
        print("%s ====> %s/%s (%i de %i)" %
              (file, destination, file, i, quantity))
        os.rename(file, destination + "/" + file)
        i += 1
    print("\n")


def get_headers_cwd():
    """
    Return FITS headers from files on the current directory.

     Args:
        None.

    Return:
        headers -- List containing headers.
    """
    files = glob("*.fits")
    headers = [fits.getheader(file) for file in files]

    return headers


def mkdirs_list(list_of_directories):
    """
    Create all the directories from a list (giving feedback).

    Args:
       list_of_directories -- List with strings of folder path's to create.
    Return:
        None.
    """
    for i in list_of_directories:
        print("Creating directories", i)
        os.makedirs(i)
    print("\n")


def select_images(keyword, value):
    """
    Return FITS file from the current directory if keyword matches value.

    Args:
        keyword -- String with the keyword to look at the header.
        value -- String or numeric containing value to match.

    Return:
        matches -- List containing string of the name of FITS files.
    """
    files = glob("*.fits")
    headers = get_headers_cwd()
    matches = [file for header, file in zip(headers, files)
               if header[keyword] == value]
    return matches


def sep_by_object(folder="./"):
    """
    Create folders structure and organize files by using the OBJECTS keyword on
    the FITS files of the given folder.

    Args:
        folder -- String containing folder to separate FITS (default is
                  current folder).
    Return
        None.
    """
    current_folder = os.getcwd()
    os.chdir(folder)

    headers = get_headers_cwd()
    objcts = set([obj["OBJECT"] for obj in headers])

    print("Object observed: ", objcts)

    mkdirs_list(objcts)

    for obj in objcts:
        move_files(select_images("OBJECT", obj), obj)
        headers = get_headers_cwd()

    os.chdir(current_folder)


def sep_by_filter(folder="./"):
    """
    Create folders structure and organize files by using the FILTER keyword on
    the FITS files of the given folder.

    Args:
        folder -- String containing folder to separate FITS (default is
                  current folder).

    Return
        None.
    """
    current_folder = os.getcwd()
    os.chdir(folder)

    headers = get_headers_cwd()
    filters = set([obj["FILTER"] for obj in headers])

    print("Images on filters: ", filters, "\n")

    mkdirs_list(filters)

    for f in filters:
        move_files(select_images("FILTER", f), f)
        headers = get_headers_cwd()

    os.chdir(current_folder)


def sep_object_by_filter(folder="./"):
    """
    Given path of folder with objects sub-folders, separate FITS files in
    folders by filters

    Args:
        folder -- String containing folder to separate FITS (default is
                  current folder).

    Return:
        None.
    """

    current_folder = os.getcwd()
    os.chdir(folder)

    objects_folder_list = os.listdir()

    for folder in objects_folder_list:
        print("Organizing images of ", folder, "\n")
        sep_by_filter(folder)
        print("\n")

    os.chdir(current_folder)


def sep_by_exptime(folder="./"):
    """
    Create folders structure and organize files by using the EXPTIME keyword on
    the FITS files of the given folder.

    Args:
        folder -- String containing folder to separate FITS (default is
                  current folder).

    Return:
        None.
    """
    current_folder = os.getcwd()
    os.chdir(folder)

    headers = get_headers_cwd()
    exptimes = set([obj["EXPTIME"].split(",")[0] for obj in headers])

    print("Exptimes for the object:\t", exptimes, "\n")

    mkdirs_list(exptimes)

    for expt in exptimes:
        move_files(select_images("EXPTIME", expt), expt)
        headers = get_headers_cwd()

    os.chdir(current_folder)

# Functions to deal with calibration files


def imstat(fits_file):
    """
    Printa em tela e retorna estatísticas da imagem em um dicionário
    Print pixel statistics from given FITS file and return a dictionary with it.
    
    Args:
        fits_file -- String containing path to FITS file to examine.
    
    Return:
        stats -- Dictionary containing median, mean, std, min, max
    """
    image = fits.getdata(fits_file)
    print("Image: %s" % (fits_file))
    print("Median: " + str(np.median(image)) + " counts")
    print("Mean: " + str(np.mean(image)) + " counts")
    print("Std: " + str(np.std(image)) + " counts")
    print("Min: " + str(np.min(image)) + " counts")
    print("Max: " + str(np.max(image)) + " counts")
    print("\n")

    stats = {"median": np.median(image),
             "mean": np.mean(image),
             "std": np.std(image),
             "min": np.min(image),
             "max": np.max(image)
            }

    return stats


def make_MasterBias(bias_folder, out_folder):
    """
    Given path to folder containing bias files, generates master bias file on 
    specified folder.

    Works by creating image cube with all images and combining on the 0th axis
    by the median.

    Args:
        bias_folder -- String with path to the folder containing the bias files.
        out_folder -- String with path to write the generated master bias.
    
    Return:
        out -- String with the path to the created file.
    """
    current_folder = os.getcwd()
    os.chdir(bias_folder)

    out = out_folder + "master_bias.fits"

    print("Generating master bias on file: ", out)

    files = os.listdir()
    ref_header = fits.getheader(files[0])
    NCOMBINE = len(files)

    print("Loading and stacking %i images ... \n" % (NCOMBINE))
    bias_cube = np.stack([fits.getdata(image) for image in files], axis=0)

    print("Extracting medians ... \n")
    master_bias = np.median(bias_cube, axis=0)

    now = dt.now().strftime("%B %d, %Y")  # Getting time stamp

    ref_header["NCOMBINE"] = NCOMBINE
    ref_header["MASTER_BIAS"] = "Done. %s" % (now)

    print("Writing FITS ... \n")
    fits.writeto(out, master_bias, ref_header)

    print("Generating master bias: %s \n Count statistics: \n" % out)
    imstat(out)

    os.chdir(current_folder)

    return out


def make_MasterFlat(flat_folder, out_folder, master_bias):
    """
    Given path to folder containing flat images, use supplied master bias to 
    generate master flat.

    FITS files are combined by median, bias subtracted and normalized by the 
    mean of pixel statistics. Header is an updated version of hte first FITS.

    Args:
        flat_folder -- String with path to flat folder.
        out_folder -- Sring with path to folder to write resulting file.
        master_bias -- String with path to master bias. 

    Return:
        file_name -- String with name of resulting file.
    """
    current_folder = os.getcwd()
    os.chdir(flat_folder)

    files = os.listdir()
    ref_header = fits.getheader(files[0])
    band = ref_header["FILTER"]

    master_bias = fits.getdata(master_bias)
    NCOMBINE = len(files)

    flat_cube = np.stack([fits.getdata(image) for image in files], axis=0)

    master_flat = np.median(flat_cube, axis=0) - master_bias

    mean = np.mean(master_flat)

    norm_master_flat = master_flat / mean

    file_name = out_folder + "master_flat_%s.fits" % (band)

    now = dt.now().strftime("%B %d, %Y")

    ref_header["NCOMBINE"] = NCOMBINE
    ref_header["MASTER_FLAT"] = "Done. %s" % (now)

    fits.writeto(file_name, norm_master_flat, ref_header)

    imstat(file_name)

    os.chdir(current_folder)

    return file_name


def make_MasterFlat_all(flats_folder, out_folder, master_bias):
    """
    Given path of folder with flats separated in folders by filters, and master
    bias to apply, it create all flats and write on the passed path. 

    Args:
        flats_folder -- String with path to the folder with the flats.
        out_folder -- String with path to write flats.
        master_bias -- String with path to master bias.

    Return:
        mflat_dict -- Dictionary containing path to each flat of each filter.
    """

    current_folder = os.getcwd()

    os.chdir(flats_folder)
    sub_folders = os.listdir()

    mflat_dict = {}

    for folder in sub_folders:
        print("Making master flat on filter:", folder)
        mflat_dict[folder] = make_MasterFlat(folder, out_folder, master_bias)
        print("\n")

    os.chdir(current_folder)

    return mflat_dict


def ccdproc(image_file, out_path, master_bias, master_flat):
    """
    Given path to FITS file applies given calibration files (bias and flat).
    
    Args:
        image_file -- String containing FITS file path.
        out_path -- String with exit name for generated file.
        master_bias -- String with path to master bias.
        master_flat -- String with path to master flat.

    Return:
        None.
    """
    mbias = fits.getdata(master_bias)
    mflat = fits.getdata(master_flat)

    header = fits.getheader(image_file)
    image = fits.getdata(image_file)

    print("Processing image: %s ..." % (image_file))

    proc_image = (image - mbias) / mflat

    out = out_path + "r_%s" % (image_file)

    # Updating header

    now = dt.now().strftime("%B %d, %Y")

    header["CCDProc"] = "Done: %s" % (now)

    fits.writeto(out, proc_image, header)


def ccdproc_all(folder_path, out_path, master_bias, master_flat):
    """
    Apply calibrations for all FITS files in a folder given path to it and to
    calibration files.

    Args:
        folder_path -- String with path to folder.
        out_path -- String wit path to exit folder.
        master_bias -- String with path to master bias.
        master_flat -- String with path to master flat.

    Return:
        None.
    """
    current_folder = os.getcwd()
    os.chdir(folder_path)

    images = os.listdir()
    images.sort()

    ref_header = fits.getheader(images[0])
    band = ref_header["FILTER"]

    N = len(images)

    print("Processing %i images on filter %s" % (N, band))

    for image in images:
        ccdproc(image, out_path, master_bias, master_flat)

    os.chdir(current_folder)


def ccdproc_all_filters(folder_path, out_path, master_bias, master_flat_dict):
    """
    Apply calibration files for every FITS file in every folder containing
    images on a given filter (use folder name as guide to select flat to use).

    Args:
        folder_path -- String with path to folder.
        out_path -- String wit path to exit folder.
        master_bias -- String with path to master bias.
        master_flat_dict -- Dictinary to be returned out of make_MasterFlat_all.

    Return:
        None.
    """
    current_folder = os.getcwd()
    os.chdir(folder_path)

    filters = os.listdir()

    for band in filters:
        master_flat = master_flat_dict[band]
        ccdproc_all(band, out_path, master_bias, master_flat)
        print("\n")

    os.chdir(current_folder)


def initial_reduction(observation_folder="./", backup=True):
    """
    Complete initial processing of observation folder. It organizes files on 
    folders both by object and filter, generate master calibration files, apply
    these files on the images taking into consideration the filter.

    Calibration operation is : (image - master_bias)/master_flat

    ATTENTION !!! It works with the standard for header use adopted on
                  mission OI2018B-011. Given OPD header format.

    Args:
        observation_folder -- String with path to the folder with files from 
                              night run.
    Return:
        None.
    """
    # Implement backup functionality here 

    os.chdir(observation_folder)

    # Defining folder structure

    root = os.getcwd()
    bias_folder = root + "/calibration/bias"
    flat_folder = root + "/calibration/flat"
    master_folder = root + "/calibration/master/"
    others_folder = root + "/others"
    raw_science_folder = root + "/science/raw"
    reduced_science_folder = root + "/science/reduced/"

    folders_list = [bias_folder, flat_folder, master_folder,
                    others_folder, raw_science_folder, reduced_science_folder]

    print("Creating folder structure ... \n")

    mkdirs_list(folders_list)

    # Looking at FITS files to organize calibration files (bias and flat)
    
    headers = get_headers_cwd()
    N = len(headers)

    bias_images = select_images("OBJECT", "bias")
    flat_images = select_images("OBJECT", "flat")

    print("Organizing calibration files ... \n")

    move_files(bias_images, bias_folder)
    move_files(flat_images, flat_folder)

    print("Separating flats by filter ... \n")

    sep_by_filter(flat_folder)

    # Organizing remaining images on science and others

    headers = get_headers_cwd()  # Updating headers

    science_images = [i["IMAGE"]+".fits" for i in headers
                      if i["COMMENT"][0].split("'")[1].strip() == "science"]
    other_images = [i["IMAGE"]+".fits" for i in headers
                    if i["COMMENT"][0].split("'")[1].strip() != "science"]

    # Used an explicit list comprehension instead of the function select_images
    # because of OPD comment format.

    # Keeping up the organization ...

    print("Moving science and other images ... \n")

    move_files(science_images, raw_science_folder)
    move_files(other_images, others_folder)

    print("Separating images by object ... \n")

    sep_by_object(raw_science_folder)
    sep_by_object(others_folder)

    print("Separating science images by filter ... \n")

    sep_object_by_filter(raw_science_folder)

    # File organized. Starting to generate calibration files.

    print("Generating calibration files ... \n")

    mbias = make_MasterBias(bias_folder, master_folder)

    mflat_dict = make_MasterFlat_all(flat_folder, master_folder, mbias)

    # Calibration files done. Starting to apply calibration on science images.

    print("Applying calibration files to science images ... \n ")

    os.chdir(raw_science_folder)
    objcts = os.listdir()

    for objct in objcts:
        print("Applying calibrations to object %s ... \n" % objct)
        ccdproc_all_filters(objct, reduced_science_folder, mbias, mflat_dict)

    print("All images processed !")

    # Images processed. Let's do the final organization

    os.chdir(root)

    print("Final organization ...")

    sep_by_object(reduced_science_folder)
    sep_object_by_filter(reduced_science_folder)

    # Add separation by exposure time here

    os.chdir(root)

    print("Reduction finished. %i FITS files where processed." % (N))
