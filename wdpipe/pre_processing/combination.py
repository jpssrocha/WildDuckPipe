"""
Functions to combine batches of images.
"""
import numpy as np
from astropy.io import fits
import os

from wdpipe.utils.context_managers import indir


def group_images(final_selection, exptime, n=5):
    """
    Given a final selection dataframe (a filtered inspection dataframe
    generated with the function `.inspection.inspect`) and the exposure time of
    the images, separate images into blocks that are separated by `n*exptime`
    units of time.
    
    Parameters
    ----------
        final_selection: pd.DataFrame
            Parameters dataframe of the final data selection.
                
        exptime: float
            Exposure time in seconds.
            
        n: int, default: 5
            number of exposure times of separation in time to define an
            observation block.
            
    Returns
    -------
        group_list: list of lists
            Return list containing lists of filenames that represents an
            observation block.
    """
    # Set delta
    delta_jd = exptime/(24*60*60)
    
    # Find places to break
    break_mask = final_selection.jd.diff() > n*delta_jd
    
    # Find indexes of break points
    ind = np.where(break_mask)[0]
    indexes = np.concatenate(([0], ind, [len(final_selection)]))
    
    # Loop over indexes and select blocks
    groups = []
    lens = []
    for i in range(len(indexes) - 1):
        len_ = len(final_selection.iloc[indexes[i]:indexes[i+1]])
        lens.append(len_)

        if len_ > 1:
            groups.append(final_selection.iloc[indexes[i]:indexes[i+1]])
        else:
            print("Escaping group of 1 image")
        
    print(f"Group sizes: {lens}")
        
    if sum(lens) != len(final_selection):
        raise Exception("Groups aren't summing up to the lenght of the selection. Review the data.")
    
    return groups


def generate_combination_bins(data_folder, final_selection, exptime, bin_size, overlap, n=5):
    """
    Calculate combination bins and generate a file for each combination bin in
    a given folder.

    The files will be on a folder called `bins` inside the `data_folder`.
    
    Parameters
    ----------
        data_folder: str
            Path to the data

        final_selection: pd.DataFrame
            Parameters dataframe of the final data selection.
                
        exptime: float
            Exposure time in seconds.

        bin_size: int
            Desired size for the bins.

        overlap: int
            Amount of overlap between images.
            
        n: int, default: 5
            number of exposure times of separation in time to define an
            observation block.

    File transformations
    --------------------
        Create a folder called `bins` and fill it with one file with each
        combination of files.
            
    Returns
    -------
        bins: list of lists
            Return list containing lists of filenames that represents
            combination bin.
    """
    
    blocks = group_images(final_selection, exptime, n=n)
    
    with indir(data_folder):
        
        if not os.path.exists("bins"):
            os.mkdir("bins")
        
        for i, block in enumerate(blocks, start=1):
            index_chunks = chunk_collection(block.index, bin_size, overlap=overlap)
            usable_index_chunks = [chunk for chunk in index_chunks if len(chunk) == bin_size]

            for j, chunk in enumerate(usable_index_chunks, start=1):
                (final_selection.loc[chunk].
                 file.
                 to_csv(f"bins/group-{i:04}_bin-{j:04}.txt", header=False, index=False))
            
    return usable_index_chunks


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
    with indir(images_folder):

        os.mkdir(out_folder)

        # Load Batches
        batches = []
        files = os.listdir(batches_folder)
        files.sort()

        for batch in files:
            with open(batches_folder + "/" + batch) as f:
                batches.append([line.strip() for line in f])

        # Define new stem name
        ref_file = batches[0][0].split("_")
        stem = f"final_{ref_file[1]}_{ref_file[2]}"
        N = len(batches)

        # For each batch combine_batch them save results
        for i, batch in enumerate(batches, start=1):
            new_name = f"{stem}_{i:04}"
            print(f"Combining batch: {batch}")
            print(f"Creating image: {new_name} ({i} de {N})")
            matrix, new_header = combine_batch(batch, new_name)
            fits.writeto(f"{out_folder}/{new_name}.fits", matrix.astype(np.float32), header=new_header)

        new_fits = os.listdir(f"{images_folder}/{out_folder}")
        new_fits.sort()


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
