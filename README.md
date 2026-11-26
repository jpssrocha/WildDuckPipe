# Wild Duck Pipe

**A Python pipeline for CCD image reduction and time-series photometry of the
Wild Duck cluster (M11).**

![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-archived-lightgrey)

Wild Duck Pipe turns a folder of raw FITS frames from an observing night into
calibrated, aligned, combined images and photometry tables. It was written to
replace a manual IRAF workflow with a scriptable Python pipeline that could be
driven from a notebook or the console.

The project started during an undergraduate scientific-initiation project and
was later extended by a colleague during his master's research, using
observations from the OPD/LNA 0.6 m (B&C) and 1.6 m (PE) telescopes.

## What it does

| Stage | Module | Description |
| --- | --- | --- |
| Organization | `pre_processing.file_organization` | Copies a night run into a `bias/`, `flat/`, `reduced/` tree and writes night-log metadata. |
| Calibration | `pre_processing.ccdred` | Overscan/trim correction, master bias and normalized flat generation, `ccdproc`-style calibration. |
| Alignment | `pre_processing.alignment` | Registers frames to a reference image with `astroalign`. |
| Combination | `pre_processing.combination` | Groups frames in time, builds combination bins, and median-combines them. |
| Inspection | `inspection.inspect` | Extracts basic statistics, sky background/sigma, and Moffat FWHM per frame. |
| Filtering | `inspection.filtering` | Interactive cuts on the inspection table to discard poor frames. |
| Photometry | `photometry.aperture_phot` | `DAOStarFinder` catalog plus aperture photometry into a light-curve table. |
| Differential photometry | `photometry.differential_phot` | Selects stable reference stars and produces differential light curves. |
| Astrometry | `astrometry.add_astrometry` | Converts X/Y source positions to RA/Dec using a WCS. |

## Project status

This is a **research prototype**, archived after the original projects ended.
It is intentionally tailored to the header and filename conventions used at
OPD/LNA (see [`docs/dev/design_doc.md`](docs/dev/design_doc.md)); it is not a
general-purpose reduction pipeline. A more flexible successor was started
separately.

Known limitations:

- The reduction path is tuned to the OPD header keywords and filename
  conventions used for these runs; full multi-extension (MEF) support was
  planned but not completed.
- Aperture photometry depends on an external, unpackaged module (see below).
- The codebase is exploratory research code and does not ship an automated
  test suite.

## Installation

Requires **Python 3.12+** and [**uv**](https://docs.astral.sh/uv/). The Python
version is pinned in `.python-version`.

```bash
# Install uv if you don't have it yet
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/jpssrocha/WildDuckPipe.git
cd WildDuckPipe
uv sync
```

`uv sync` creates `.venv/` from `pyproject.toml` and the committed `uv.lock`.
Verify the environment:

```bash
uv run python -c "import wdpipe; print(wdpipe.__doc__)"
```

> The repository is used from its root and is not published as a wheel on
> PyPI. Run your scripts from the root, or set `PYTHONPATH=.` when running
> them from another directory.

### Optional: aperture-photometry backend

`wdpipe.photometry.aperture_phot` uses the IRAF-style photometry helper from
[`spacetelescope/wfc3_photometry`](https://github.com/spacetelescope/wfc3_photometry).
That project has no packaging metadata and is not on PyPI, so it cannot be
declared as a normal dependency. Clone it into `third_party/` and expose it on
`PYTHONPATH`:

```bash
mkdir -p third_party
git clone https://github.com/spacetelescope/wfc3_photometry.git third_party/wfc3_photometry
export PYTHONPATH="$PWD/third_party:$PYTHONPATH"
```

The rest of `wdpipe` imports without it; only the aperture-photometry call
raises a descriptive error when the module is missing.

> **photutils 2.x compatibility:** the upstream helper predates photutils 2 and
> imports `aperture_photometry`, `CircularAperture`, and `CircularAnnulus` from
> the `photutils` root. With the pinned photutils 2.x, patch the checkout:
>
> ```bash
> sed -i 's/from photutils import aperture_photometry/from photutils.aperture import aperture_photometry/' \
>     third_party/wfc3_photometry/photometry_tools/photometry_with_errors.py
> sed -i 's/from photutils import CircularAnnulus, CircularAperture/from photutils.aperture import CircularAnnulus, CircularAperture/' \
>     third_party/wfc3_photometry/photometry_tools/phot_wrapper.py
> ```

## Quickstart

### 1. Reduce a night run

```python
from wdpipe.pre_processing.processes import initial_reduction

initial_reduction("/path/to/18out30")
```

`initial_reduction` organizes the raw files, builds master bias/flats, applies
the calibrations, and writes the result to `r_18out30/` next to the input
folder:

```text
r_18out30/
├── calibration/   # bias/ and flat/<filter>/
├── master/        # master_bias.fits, master_flat_<filter>.fits
├── reduced/       # calibrated science frames
└── *_night.log    # per-frame metadata and a human-readable summary
```

### 2. Inspect image quality

```python
from wdpipe.inspection.inspect import inspect

parameters = inspect("r_18out30/reduced", "refs.csv", "parameters.csv")
```

`refs.csv` lists reference patches with columns `kind,x,y`, where `kind` is
`star` or `sky`. The returned table contains basic statistics, sky background,
sky sigma, and FWHM for each frame.

### 3. Aperture and differential photometry

```python
from pathlib import Path

import pandas as pd

from wdpipe.photometry.aperture_phot import get_catalog, assemble_lightcurve
from wdpipe.photometry.differential_phot import differential_photometry

ref_frame = "r_18out30/reduced/OI2018B-011_2018-10-16_0001.fits"
pars = pd.read_csv("parameters.csv", index_col="file")

catalog, sources = get_catalog(ref_frame, pars.loc[Path(ref_frame).name])
light_curve = assemble_lightcurve("r_18out30/reduced", catalog, "parameters.csv")

ref_mags, ref_stars, diff = differential_photometry(light_curve, n=100)
```

## Repository layout

```text
.
├── wdpipe/
│   ├── pre_processing/   # organization, night logs, calibration, alignment, combination
│   ├── inspection/       # statistics, sky/FWHM estimates, quality filtering
│   ├── photometry/       # aperture and differential photometry
│   ├── astrometry/       # WCS-based coordinate annotation
│   └── utils/            # shared helpers
├── docs/
│   ├── dev/              # design document and development notebooks
│   └── related_reports/  # scientific-initiation reports (Portuguese)
├── examples/             # cleaned marimo example
├── pyproject.toml
├── uv.lock
└── README.md
```

## Data conventions

The pipeline expects the OPD/LNA conventions used since mission `OI2018B-011`:

- Filenames follow `OI2018B-011_2018-10-16_0001.fits` (mission, date, frame
  number).
- `OBJECT` identifies the calibration type (`BIAS`, `FLAT`) or the science
  target.
- `COMMENT` marks science frames; calibration frames are copied and reduced
  separately.
- `BIASSEC`/`TRIMSEC` describe the overscan and trim sections.
- Light-curve tables are CSV files with columns
  `RA, DEC, ID, Xcenter, Ycenter, MAG1, ERR1, ...`.

The full rationale and conventions are in
[`docs/dev/design_doc.md`](docs/dev/design_doc.md).

## Examples and development notes

- [`examples/align_and_combine.py`](examples/align_and_combine.py) — a cleaned
  marimo notebook demonstrating alignment and combination. Run it with
  `uv run marimo edit examples/align_and_combine.py` and set `WDPIPE_DATA` to a
  folder of reduced frames.
- [`docs/dev/notebooks/`](docs/dev/notebooks/) — exploratory notebooks from the
  original development.
- [`docs/dev/notebooks/image-reduction-example-18out30.ipynb`](docs/dev/notebooks/image-reduction-example-18out30.ipynb)
  — end-to-end walkthrough of the 2018-10-30 night, preserved from the
  original environment (update its hard-coded paths before running).
- [`docs/related_reports/`](docs/related_reports/) — the scientific-initiation
  reports that document the project.

## Acknowledgments

Built on the scientific Python stack: `astropy`, `ccdproc`, `astroalign`,
`photutils`, `pandas`, `numpy`, `matplotlib`, and `scikit-image`. Aperture
photometry uses the IRAF-style helper from
[`spacetelescope/wfc3_photometry`](https://github.com/spacetelescope/wfc3_photometry).
Observations were obtained at the Pico dos Dias Observatory (OPD/LNA).

## License

MIT — see [LICENSE](LICENSE).
