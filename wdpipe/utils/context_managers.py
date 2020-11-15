import os
from contextlib import contextmanager

@contextmanager
def indir(directory):
    """
    Context manager to enter a folder to something than return to the
    original folder.

    Parameters
    ----------
        directory : str
            Path to the folder to get in.

    Returns
    -------
        None.
    """
    try:
        cwd = os.getcwd()
        os.chdir(directory)
        yield
    finally:
        os.chdir(cwd)
