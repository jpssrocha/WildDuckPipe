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


The final goal is to have a pipeline framework on which will be possible
to pass the path to the folder with the original files from an observing
run and have back the final results (reduced images, photometry tables,
calibrations and so on) with a simple command.


In a first moment it will be developed to work with images from the Pico
dos Dias Observatory (OPD) because it is using the same header keywords as
there. But the final goal a generic way of passing the keywords allowing the
reduction of FITS images from anywhere that can be reduced on a standard way.

Main goal is to work with the following instruments:

- CAM(1-2)@OPD
- SPARC4@OPD (?)
- SAMI@SOAR
- Goodman@SOAR (imaging mode)


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
- Creation of a database using meta-data

## Image processing tools

- Overscan and trim correction (Done)

- Generation of master calibration images (Done)
    - Master Bias (Done)
    - Master Normalized Flat (Done)

- Application of calibrations (Done)
    - Bias subtraction (Done)
    - Flat normalization (Done)
    - Iraf CCDPROC like task (re implementing using astropy's ccdproc)

- Image alignment
    - For rich fields (e.g. stellar clusters) (astroalign) (To re implement to work w/ MEF'S)
    - For poor fields (e.g. field variable star) (IRAF's imalign like)

- Image combination (To re implement using ccdproc)

- Automatic astrometry (astrometry.net) 

## Data inspection tools

- Extraction of basic statistics (Done)

- Robust automatic estimations (Done ?)
    - Sky sigma
    - FWHM (OK)

- Image quality visualization plots


## Data reduction tools

- Photometry
    - Aperture photometry
    - PSF photometry
    - Differential Image Analysis (maybe)
    - Photometric calibrations

## Analysis tools

- Light Curve
    - Generation of artificial reference star
    - Differential photometry
    - Variability detection
    - Time series plot

- Color Magnitude Diagram visualization

# Desired features

- File organization to facilitate manual inspection
- Fully automated pre processing of FITS files
- Support for multi-extension files (MEF)
- Option to use shell interface
- Built using official astropy packages (to leverage improvements from then)
- Organization tools to be used in a project
