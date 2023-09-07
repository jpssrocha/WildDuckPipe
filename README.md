# Wild Duck Pipe

**UNDER CONSTRUCTION !!!**

This project was started by the necessity of a framework that allows
photometric image reduction and analysis inside Python, being able to taking
advantage of the language's flexibility and large ecosystem. It leverages the
following packages (beyond the scipy stack):

- pandas
- astropy
- ccdproc
- astroalign
- astrometry.net
- photutils

To work with the aperture photometry is also leveraged the code at:

> https://github.com/spacetelescope/wfc3_photometry/tree/master


The final goal is to have a pipeline framework on which will be possible
to pass the path to the folder with the original files from an observing
run and have back the final results (reduced images, photometry tables,
calibrations and so on) with a simple command.


In a first moment it will be developed to work with images from the Pico
dos Dias Observatory (OPD) because it is using the same header keywords as
there. But the final goal a generic way of passing the keywords allowing the
reduction of FITS images from anywhere that can be reduced on a standard way.

Main goal is to work with the following instruments:

- CAM 1@OPD
- CAM 2@OPD

Testing and development of the software is being done through the exploration
many aspects of a time-series dataset collected over 10 days for M11 (the
Wild Duck cluster) using the B&C (0.6 m) and PE (1.6 m) telescopes equipped
with an imaging setup (CCD, filter wheel and guiding camera). Therefore some
tools specific to this can be included, such as time-series manipulation tools,
tools to organize information about a survey, tools to deal with cluster data,
and so on.


# Tools to integrate

## Organization tools

- Organization in folders (Done)
- Generation of night run meta-data (Done)
- Creation of a database using meta-data (Done)

## Image processing tools

- Overscan and trim correction (Done)

- Generation of master calibration images (Done)
    - Master Bias (Done)
    - Master Normalized Flat (Done)

- Application of calibrations (Done)
    - Bias subtraction (Done)
    - Flat normalization (Done)
    - Iraf CCDPROC like task (Done)

- Image alignment (Done)

- Image combination (Done)

- Automatic astrometry (via astrometry.net)  (TODO)

## Data inspection tools

- Extraction of basic statistics (Done)

- Semi-automatic estimations (Done)
    - Sky sigma (Done)
    - FWHM (Done)

- Image quality visualization plots (Done)


## Data reduction tools

- Photometry
    - Aperture photometry (Done)
    - PSF photometry
    - Photometric calibrations

## Analysis tools

- Light Curve
    - Generation of artificial reference star (Done)
    - Differential photometry (Done)
    - Variability detection
    - Time series plot (Done)


# Desired features

- File organization to facilitate manual inspection (Done)
- Fully automated pre processing of FITS files (Done)
- Support for multi-extension files (MEF) (Will be added on version 2)
- Built using official astropy packages (to leverage improvements from then)
