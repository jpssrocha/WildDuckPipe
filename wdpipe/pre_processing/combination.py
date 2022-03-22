"""
Functions to combine batches of images.
"""
import numpy as np
from astropy.io import fits
import os


def combine_batch(batch, update_name):
    """
    From a text file containing FITS files names, combine all images and
    generate new reference header.  Give back the new matrix and header. Used
    from within the folder with the images

    Args:
        batch -- List of strings with path to batch text file.
        update_name -- String with the exit name.

    Return:
        combination -- 2D numpy array containing combined image
        ref_header -- Astropy header object with updated info.
    """
    # Load images and headers

    images = [fits.getdata(file) for file in batch]
    headers = [fits.getheader(file) for file in batch]

    #  New parameters
    airmasses = np.array([np.float64(header["AIRMASS"]) for header in headers])
    jds = np.array([np.float64(header["JD"]) for header in headers])
    ncombine = len(images)
    middle = int(ncombine/2)
    date = headers[middle]["DATE-OBS"]

    # Generate reference header
    ref_header = headers[middle]
    ref_header["JD"] = jds.mean()
    ref_header["AIRMASS"] = airmasses.mean()
    ref_header["NCOMBINE"] = ncombine
    ref_header["DATE-OBS"] = date
    for (i, file) in enumerate(batch, start=1):
        ref_header[f"IMCMB{i}"] = file
    ref_header["IMAGE"] = update_name

    # Combine images

    cube = np.stack(images, axis=0)

    combination = np.median(cube, axis=0)

    return (combination, ref_header)


def combine_batches(images_folder, batches_folder="batches", out_folder="combinated"):
    """
    From a text file containing FITS files names, combine all images and
    generate new reference header.  Give back the new matrix and header.

    New name definition takes old name (following the conventions) strip the
    number part and create a new based on the combination order.

    OBS1: Expects that the batch folder is already created.

    Args:
        images_folder -- String with path to the folder with the images.
        batches_folder -- Strings with path to batch folder files relative to
                          the images folder.
        out_folder -- String with the exit folder name relative to .

    Return:
        List of strings with path to created files.

    File transformations:
        Write new FITS files for the combinations.
    """
    cwd = os.getcwd()
    os.chdir(images_folder)

    os.mkdir(out_folder)

    # Load Batches
    batches = []
    for batch in os.listdir(batches_folder):
        with open(batches_folder + "/" + batch) as f:
            batches.append([line.strip() for line in f])

    # Define new stem name
    ref_file = batches[0][0].split("_")
    stem = f"final_{ref_file[1]}_{ref_file[2]}"
    N = len(batches)

    # For each batch combine_batch them save results
    for i, batch in enumerate(batches, start=1):
        new_name = f"{stem}_{i:04}"
        print(f"Creating image: {new_name} ({i} de {N})")
        matrix, new_header = combine_batch(batch, new_name)
        fits.writeto(f"{out_folder}/{new_name}.fits", matrix.astype(np.float32), header=new_header)

    new_fits = os.listdir(f"{images_folder}/{out_folder}")
    new_fits.sort()

    os.chdir(cwd)

    return new_fits


def chunk_collection(collection, chunk_size, overlap=0):
    """
    Given a `collection` it will divide it into chunks of `chunk_size` with an
    option to have an `overlap` between chunks. It will discard the chunks that
    have an index that is out of bounds.

    Arguments
    ---------
        collection: list like object
            Collection to chunk.
        chunk_size: int
            Size of the chunks.
        overlap: int, default=0
            Number of element to overlap.
    Returns
    -------
        chunks: list of lists
            List containing the chunks.
    """
    if overlap >= chunk_size:
        raise Exception("Block size greater or equal the overlap will generate infinite loop")
    # Correction due to implicit subtraction on the loop
    overlap = overlap - 1

    # First element
    indexes = [list(range(0, chunk_size))]

    b = 0  # Starting b
    while b < len(collection):
        # Fist limit: last element of the last list minus overlap
        a = indexes[-1][-1] - overlap
        b = a + chunk_size  # Second limit with step size
        # There is an implicit minus here since range goes up to b-1
        indexes.append(list(range(a, b)))

    # Filtering
    indexes = [index for index in indexes if not len(collection) in index]

    chunks = []
    for index in indexes:
        chunks.append([collection[i] for i in index])

    return chunks
