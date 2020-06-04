# Wild Duck Pipe

This project was started by the necessity of a framework that allows data reduction and analysis
inside Python, being able to taking advantage of the language's flexibility.

The final goal is to have a framework on which will be possible to take the original files from 
an observing run and have back the final results (reduced images, photometry tables, calibrations
and so on) with a simple command.

# Tools to integrate:

## Image processing tools;

	- Generation of master calibration images;
		- Bias;
		- Dark;
		- Normalised Flat;

	- Application of calibrations;
		- Bias and Dark subtraction;
		- Flat normalization;

	- Image combination;

	- Organization in folders;

## Astrometry;
	
	- Automatic Plate-solving (astrometry.net); 

## Data inspection tools;

	- Extraction of basic statistics;

	- Robust automatic estimations;
		- Sky sigma;
		- FWHM;

	- Image quality visualization plots;


## Data reduction tools;

	- Photometry;
		- Aperture photometry;
		- PSF photometry;
		- Differential photometry;
		- Photometric calibrations;

## Analysis tools;

	- Light Curve;
		- Generation of artificial reference star;
		- Variability detection;
		- Time series plot;

	- Color Magnitude Diagram visualization;


