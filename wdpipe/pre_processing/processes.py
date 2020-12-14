"""
Module containing the utility functions to perform automated reduction using
the code from this sub-package.
"""
from . import ccdred
from .nightlog import get_log
from .file_organization import organize_nightrun, sep_by_kw

def initial_reduction(nightrun_folder):
    """
    Given a folder perform all the initial reduction process:
        - Organize files
        - Generate masters
        - Correct overscan
        - Apply masters calibration files

    Parameters
    ----------
        nightrun_folder : str
            Path to the folder to reduce

    File transformations
    --------------------
        Create a copy of all files, organize them into a folder structure,
        create master files and overwrite all files with the calibrations
        applied.

    Returns
    -------
        None
    """

    print(f"Starting to process folder {nightrun_folder}")
    
    folders = organize_nightrun(nightrun_folder)

    # Correcting bias and combining into master

    print(f"Processing bias images into master bias")

    bias_list = [str(path) for path in folders["bias"].glob("*.fits")]

    for im in bias_list:
        ccdred.correct_overscan(im)

    mbias = ccdred.make_mbias(bias_list, folders["master"])

    #  Correcting flats and combining into masters

    print("Processing flat images")

    mflats = {}
    for filt in structure["flat"]:
        flat_list = [str(path) for path in structure["flat"][filt].glob("*.fits")]
        for im in flat_list:
            ccdred.correct_overscan(im)
        mflats.update(ccdred.make_mflat(flat_list, mbias, structure["master"], filt))
    

    #  Correct overscan of sci images

    sci_list = [str(path) for path in folders["reduced"].glob("*.fits")]

    print(f"Processing {len(sci_list)} science images")

    for im in sci_list:
        ccdred.correct_overscan(im)


    log_df, _ = get_log(structure["reduced"], write=False)

    #  Find unique filters
    uniq = log_df["FILTER"].unique()

    #  Use ccdred in each one

    for filt in uniq:
        # Take filenames on the filters
        files = log_df[log_df["FILTER"] == filt].index
        #  Apply ccdproc
        for file in files:
            ccdred.ccdred(str(structure["reduced"] / file), mbias, mflats[filt])

    # Organize final results
    log_df, _ = get_log(structure["reduced"], write=False)

    # Organize objects
    print("Organizing final files into objects.")
    objects = sep_by_kw(structure["reduced"], "OBJECT")

    for obj, path in objects.items():
        # Separate object by filter
        print(f"Organizing images of {obj}")
        filters = sep_by_kw(path, "FILTER")
        for filt in filters.values():
            # Separate filters by exptime
            sep_by_kw(filt, "EXPTIME")

    # Check and remove unnecessary calibration files

    # Converting to path object

    from pathlib import Path
    from shutil import rmtree

    mbias = Path(mbias)

    # Check existance of file

    if mbias.exists():
        rmtree(folders["bias"])

    n = 0
    for flat, filter in mflats.items():
        if flat.exists():
            rmtree(folders["flat"][filter])
            n += 1

    if len(mflats) == n:
        rmtree(folders["flat"])



