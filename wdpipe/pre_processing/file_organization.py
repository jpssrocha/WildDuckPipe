"""Functions to help organize files using the log file

"""
import os
from shutil import copyfile, move
from pathlib import Path

from . import nightlog
from ..utils.context_managers import indir


def copy_files(files, destination, overwrite=False):
    """
    Move list of files to specified destination.

    Parameters
    ----------
        files : List-like object with pathlib.Path objects
            List containing strings with the address of files to copy.

        destination : pathlib.Path object
            Destination folder.

        overwrite : bool 
            Overwrite or not. Default False (not overwrite)

    Returns
    -------
        None.

    File transformations
    --------------------
        Write copies of the files to destination
    """

    quantity = len(files)
    print(f"Copying {quantity} files... \n")

    for i, file in enumerate(files, start=1):
        print(f"{file} ====> {destination}/{file.name} ({i} de {quantity})")

        dest = destination / file.name        

        if dest.exists() and not overwrite:
            print(f".Skipping {dest}: File already exists")
            continue
        
        copyfile(file, destination / file.name)
    print("\n")


def move_files(files, destination):
    """
    Move list of files to specified destination.

    Parameters
    ----------
        files : list-like object containing strings 
            Addresses of files.
            
        destination : str
            Destination folder.
            
    File transformations
    --------------------
        Move files to the specified destination

    Returns
    -------
        None.
    """
    quantity = len(files)
    print(f"Moving {quantity} files... \n")

    for i, file in enumerate(files, start=1):
        print(f"{file} ====> {destination}/{file} ({i} de {quantity})")
        move(file, str(Path(f"{destination}/{file}")))
    
    print("\n")


def sep_by_kw(folder, key):
    """
    Separate images inside a folder using the unique value of a column on a 
    nighlog.log() dataframe.
    
    Arguments
    ---------
    
    folder : str
        Path to the folder on which to separate.

    key : str
        Key on which to find unique values to separate images.
        
        File transformations
    --------------------
        Create a folder to each unique values on the choosen key, then move 
        images of each value 
        
    Returns
    -------
        new_folders : dict of pathlib.Path objects
            Path's to the created folders.
    """
    
    #  Get values
    
    log_df, _ = nightlog.get_log(folder, write=False)
    
    with indir(folder):
        
        kw_col = log_df[key]

        uniq = kw_col.unique() #  np.array of unique values

        uniq_paths = list(
                map(Path, 
                    list(map(str, uniq))
                )) #  transformed into list of Path objects

        #  Create folders relative to the path on the folder parameter

        for path in uniq_paths:
            path.mkdir(parents=True, exist_ok=True)

        #  Move files to each folder
        for uniq_value in uniq:
            matchs = kw_col[kw_col == uniq_value].index
            move_files(matchs, uniq_value)

        #  Create dict containg Path's for the created folders

        new_folders = {str(path): folder / path for path in uniq_paths}
    
    return new_folders

def organize_nightrun(folder, out_location=None):
    """
    Organize files of a night run into a folder structure in a new folder.
    
    OBS: Expecting organization from OPD's OI2018B-031 mission for folder
    and FITS headers.  Headers are read by the nightlog.get_log function to
    create a dataframe to guide the process.
    
    Parameters
    ----------
        folder : str
            Path to the night run folder to generate organized files

        out_location : str or None 
            Path to folder on which to create the reduction folder. Default
            is None, it creates the reduction folder on the same directory
            of the original.
            
    Returns
    -------
        folders: dict of pathlib.Path objects
            Path's to the created folders.
        
        
    File transformations
    --------------------
        Create new folder and copy files into an structure.
    
    """
    
    #  Small fix to avoid bug due to lacking \ or /
    folder.strip("\\").strip("/")
    folder = f"{folder}/"
    folder = Path(folder)

    #  Create log for folder
    
    print(f"Getting log for {folder} ... \n")
    
    log, log_filename = nightlog.get_log(folder, write=True)
    
    summary_filename = nightlog.get_summary(log_filename)

    
    #  Creating folder structure
    if out_location != None:
        root = Path(f"{out_location}/r_{folder.name}")
    else:
        root = Path(f"{folder.parent / ('r_' + folder.name)}")
    
    
    folders = {
        "root": root,
        "bias": root / "calibration/bias",
        "flat": root / "calibration/flat",
        "master": root / "master",
        "reduced": root / "reduced"
    }
    
    print(f"Creating new folder structure for {folder} ... \n")
    
    for path in folders.values():
        path.mkdir(parents=True, exist_ok=True)
    
    #  Copy files to the right places using the log
    
    print("Copying files to structure ... \n")
    
    #  Select files into lists
    
    bias = log[log["OBJECT"] == "BIAS"].index #  Index col is the filename
    flats = log[log["OBJECT"] == "FLAT"].index
    sci = log[log["COMMENT"] == "science"].index

    print("Copying bias ...\n")
    
    copy_files(folder / bias, folders["bias"])
    
    print("Copying flats ...\n")
    
    copy_files(folder / flats, folders["flat"])

    print("Copying science images ...\n")
        
    copy_files(folder / sci, folders["reduced"])
    
    #   Organize flat files
    
    print("Organizing flat images ...\n")

    flats = sep_by_kw(folders["flat"], "FILTER")
    folders["flat"] = flats
       
    #  Copy metadata
    
    print("Moving metadata ...\n")
    
    meta = [log_filename, summary_filename]
    # meta = list(map(str, meta))
    copy_files(meta, folders["root"])
    
    return folders


def move_lacking_fits(on_folder, fits_list, to_folder):
    """
    Given a folder, a list of FITS files on that folder and a folder on which
    to move files. Get the FITS on that folder and move those who aren't on the
    `fits_list`.
    
    obs: the to_folder path has to be relative to the on_folder

    Parameters
    ----------
        on_folder: str
            Folder to look for fits files

        fits_list: list of str
            List of FITS files to maintain

        to_folder: str
            Folder on which to move files relative to the `on_folder`.
    
    Returns
    -------
        none
    """
    from glob import glob
    from os.path import exists

    
    # Go to that folder
    with indir(on_folder):
        
        # Get all FITS
        all_fits = glob("*.fits")
        all_fits.sort()
        
        if not exists(to_folder):
            os.mkdir(to_folder)
        
        # Get lacking FITS
        lacking_fits = [file_ for file_ in all_fits if file_ not in list(fits_list)]
        
        print(f"Moving {len(lacking_fits)} FITS files from {len(all_fits)}")
        
        # Move lacking FITS
        move_files(lacking_fits, to_folder)
        
