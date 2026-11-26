"""Align and combine reduced frames.

Run with:

    uv run marimo edit examples/align_and_combine.py

Set ``WDPIPE_DATA`` to the folder that holds the reduced frames, organized as
``<filter>/<exptime>/``. The alignment step rewrites files in place and removes
the originals, so work on a copy of the data.
"""

import marimo

__generated_with = "0.17.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import os
    import sys
    from glob import glob
    from pathlib import Path

    # The repository is used from its root and is not installed as a package;
    # make that root importable when the notebook runs from examples/.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    from wdpipe.pre_processing.alignment import align_all_images
    from wdpipe.pre_processing.combination import combine_batch

    return Path, align_all_images, combine_batch, glob, mo, np, os, plt


@app.cell
def _(mo):
    mo.md(
        """
        # Align and combine reduced frames

        This notebook aligns every frame in a filter/exposure folder to a
        reference frame, then median-combines the aligned frames.

        **Warning:** alignment rewrites the FITS files in place and removes the
        originals. Point `WDPIPE_DATA` at a copy of the data.
        """
    )
    return


@app.cell
def _(Path, os):
    data_root = Path(os.environ.get("WDPIPE_DATA", "data/reduced"))
    data_root
    return (data_root,)


@app.cell
def _(data_root):
    filters = ("B", "V", "I")
    exptime = "60"
    return exptime, filters


@app.cell
def _(align_all_images, data_root, exptime, filters):
    # Align the reference filter first. The aligned frame is written with an
    # `a_` prefix and the original is removed.
    ref_folder = data_root / "V" / exptime
    ref_file = next(
        path
        for path in sorted(ref_folder.glob("*.fits"))
        if not path.name.startswith("a_")
    )

    align_all_images(str(ref_folder), ref_file=str(ref_file))
    aligned_ref = ref_folder / f"a_{ref_file.name}"

    # Align the remaining filters to the already-aligned reference frame.
    for _filt in filters:
        if _filt == "V":
            continue
        align_all_images(
            str(data_root / _filt / exptime),
            ref_file=str(aligned_ref),
        )

    return (aligned_ref,)


@app.cell
def _(combine_batch, data_root, exptime, filters, glob):
    final_images = {}

    for _filt in filters:
        files = sorted(glob(str(data_root / _filt / exptime / "*.fits")))
        final_images[_filt] = combine_batch(files, f"m6752_{_filt}")

    return (final_images,)


@app.cell
def _(final_images, np, plt):
    im = np.stack([image for image, _ in final_images.values()], axis=-1)
    im[im < 0] = 0
    im = im / np.percentile(im[:, :, 0], 99) * np.array([1, 0.50, 0.2])

    plt.imshow(im)
    plt.axis("off")
    return


if __name__ == "__main__":
    app.run()
