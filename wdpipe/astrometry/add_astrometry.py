"""
Utility funcs to add astrometry to tables.
"""
import numpy as np
from astropy.wcs import WCS


def add_astrometry(target_table_file, wcs_frame):
    """
    Given a table of sources with positions in X and Y create new table with RA
    and DEC on the first collumns.

    Parameters
    ----------

        target_table_file : str
            The address to the data table

        wcs_frame : str
            Name of FITS file with the frame of reference for the table w/ WCS
            information.

    File transformations
    --------------------

        Write updated table with a '.wcs' suffix, adding two collumns on the
        front with the DEC and RA.

    """

    data = np.loadtxt(target_table_file, delimiter=",")
    w = WCS(wcs_frame)

    x, y = data[:, 1], data[:, 2]
    RA, DEC = w.wcs_pix2world(x, y, 1)

    WC = np.vstack((RA, DEC)).transpose()

    final = np.hstack((WC, data))

    np.savetxt(target_table_file + ".wcs", final, delimiter=",")
