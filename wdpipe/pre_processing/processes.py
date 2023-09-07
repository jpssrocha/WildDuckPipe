"""
Module containing the utility functions to perform automated reduction using
the code from this sub-package.
"""
from . import ccdred
from .nightlog import get_log
from .file_organization import organize_nightrun, sep_by_kw
from pathlib import Path
from shutil import rmtree


def initial_reduction(nightrun_folder, out_location=None):
    """
    Given a folder perform all the initial reduction process:
        - Organize files
        - Generate masters (bias, flat)
        - Correct overscan
        - Apply masters calibration files

    Parameters
    ----------
        nightrun_folder : str
            Path to the folder to reduce

        out_location : str or None 
            Path to folder on which to create the reduction folder. Default
            is None, it creates the reduction folder on the same directory
            of the original.

    File transformations
    --------------------
        Create a copy of all files, organize them into a folder tree,
        create master files and overwrite all files with the calibrations
        applied.

    Returns
    -------
        None
    """

    print(f"Starting to process folder {nightrun_folder} \n")

    folders = organize_nightrun(nightrun_folder, out_location=out_location)

    # Correcting bias and combining into master

    print(f"\nProcessing bias images.\n")

    bias_list = [str(path) for path in folders["bias"].glob("*.fits")]

    mbias = ccdred.make_mbias(bias_list, folders["master"])

    #  Correcting flats and combining into masters

    print("\nProcessing flat images. \n")

    mflats = {}
    for filt in folders["flat"]:
        flat_list = [str(path) for path in folders["flat"][filt].glob("*.fits")]
        mflats.update(ccdred.make_mflat(flat_list, mbias, folders["master"], filt))

    #  Correct overscan of sci images

    sci_list = [str(path) for path in folders["reduced"].glob("*.fits")]

    print(f"\nProcessing {len(sci_list)} science images. \n")

    for im in sci_list:
        ccdred.correct_overscan(im)

    log_df, _ = get_log(folders["reduced"], write=False)

    #  Find unique filters
    uniq = log_df["FILTER"].unique()

    #  Use ccdred in each one

    for filt in uniq:
        # Take filenames on the filters
        files = log_df[log_df["FILTER"] == filt].index.tolist()

        files = [str(folders["reduced"] / file) for file in files]

        #  Apply ccdproc
        if filt in mflats:
            ccdred.ccdred_list(files, mbias, mflats[filt])

        else:
            print(f"WARNING: No flat available for {filt} filter.")


    # Organize final results
    log_df, _ = get_log(folders["reduced"], write=False)

    # Organize objects
    print("Organizing final files into objects.")
    objects = sep_by_kw(folders["reduced"], "OBJECT")

    for obj, path in objects.items():
        # Separate object by filter
        print(f"Organizing images of {obj}")
        filters = sep_by_kw(path, "FILTER")
        for filt in filters.values():
            # Separate filters by exptime
            sep_by_kw(filt, "EXPTIME")

    # Check and remove unnecessary calibration files

    # Converting to path object

    mbias = Path(mbias)

    for filter in mflats:
        mflats[filter] = Path(mflats[filter])

    # Check existance of file

    print("\nCleaning up calibration files. \n")

    n = 0
    if mbias.exists():
        rmtree(folders["bias"])
        n += 1

    for filter, flat in mflats.items():
        if flat.exists():
            rmtree(folders["flat"][filter])
            n += 1

    if len(mflats) + 1 == n:
        rmtree(folders["bias"].parent)

    print("Processing finished.")
