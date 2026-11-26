# Examples

## `align_and_combine.py`

A marimo notebook that aligns reduced frames to a reference frame and
median-combines them. It expects data organized as `<filter>/<exptime>/` and
reads the root folder from the `WDPIPE_DATA` environment variable:

```bash
export WDPIPE_DATA=/path/to/r_18out30/reduced
uv run marimo edit examples/align_and_combine.py
```

Alignment rewrites FITS files in place and removes the originals, so point
`WDPIPE_DATA` at a copy of your data.

For the full end-to-end reduction walkthrough, see
[`docs/dev/notebooks/image-reduction-example-18out30.ipynb`](../docs/dev/notebooks/image-reduction-example-18out30.ipynb).
