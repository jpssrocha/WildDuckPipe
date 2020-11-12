"""file_organization - Functions to help organize files using the log file

"""
from pathlib import Path
import pandas as pd


def mkdirs_list(list_of_directories):
    """
    Create all the directories from a list (giving feedback).

    Parameters
    ----------
       list_of_directories : List with strings of folder path's to create.

    Returns
    -------
        None.
    """
    from os import makedirs

    for directory in list_of_directories:
        print("Creating directory:", directory)
        makedirs(directory)
    print("\n")


def copy_files(files, destination):
    """
    Move list of files to specified destination.

    Parameters
    ----------
        files : List-like object with strings
            List containing strings with the address of files to copy.
        destination : str
            Destination folder.

    Returns
    -------
        None.

    File transformations
    --------------------
        Write copies of the files to destination
    """
    from shutil import copyfile
    quantity = len(files)
    print("Copying", quantity, "files... \n")

    for i, file in enumerate(files, start=1):
        print(f"{file} ====> {destination}/{file} ({i} de {quantity})")
        copyfile(file, destination + "/" + file)
    print("\n")
