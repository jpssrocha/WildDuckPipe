import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    from wdpipe.pre_processing.alignment import align_all_images
    from wdpipe.pre_processing.combination import combine_batch


    import os
    from pathlib import Path
    from glob import glob

    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    import numpy as np
    return align_all_images, combine_batch, glob, np, os, plt


@app.cell
def _(os):
    os.environ["HOME"]
    return


@app.cell
def _(al):
    al
    return


@app.cell
def _(align_all_images):
    # ref = f"/home/jpsrocha/Documents/Data/r_24ago12/reduced/NGC6752/60/V/OI2024A-030_2024-08-12_0379.fits"
    ref = "/home/jpsrocha/Documents/Data/r_24ago12/reduced/NGC6752/V/60/OI2024A-030_2024-08-12_0379.fits"

    align_all_images(f"/home/jpsrocha/Documents/Data/r_24ago12/reduced/NGC6752/V/60", ref_file=ref)
    return


@app.cell
def _(align_all_images, os):
    ref_after = "/home/jpsrocha/Documents/Data/r_24ago12/reduced/NGC6752/V/60/a_OI2024A-030_2024-08-12_0379.fits"

    align_all_images(f"{os.environ["HOME"]}/Documents/Data/r_24ago12/reduced/NGC6752/I/60", ref_file=ref_after)
    align_all_images(f"{os.environ["HOME"]}/Documents/Data/r_24ago12/reduced/NGC6752/B/60", ref_file=ref_after)
    return


@app.cell
def _(combine_batch, glob, os):

    filters = ["B", "V", "I"]
    final_images = {}

    for f in filters:
        list_of_files = glob(f"{os.environ["HOME"]}/Documents/Data/r_24ago12/reduced/NGC6752/{f}/60/*")
        final_images[f] = combine_batch(list_of_files, f"m6752_{f}")

    return (final_images,)


@app.cell
def _(final_images, np, plt):
    im =  np.stack([im for im, _ in final_images.values()], axis=-1)
    im[im < 0] = 0
    im = im/np.percentile(im[:, :, 0], 99)*np.array([1, 0.50, 0.2])
    #n = LogNorm(vmin=np.percentile(im[:, :, 2], 5), vmax=np.percentile(im[:, :, 2], 80))

    # vmin=np.percentile(im[:, :, 2], 5), vmax=np.percentile(im[:, :, 2], 80)

    # for ii in range(3):
    #     im[:, :, ii] = n(im[:, :, ii])

    plt.imshow(im,)
    return (im,)


@app.cell
def _(im):
    im.mean(axis=0)
    return


@app.cell
def _(im, plt):

    for i in range(3):
        plt.hist(im[:, :, i].ravel(), bins=50)
        plt.show()
    return


@app.cell
def _(im):
    im[:, :, 0]
    return


@app.cell
def _(im):
    im.shape
    return


if __name__ == "__main__":
    app.run()
