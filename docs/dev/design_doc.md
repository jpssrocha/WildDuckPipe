# Design Doc

This a simple doc describing quickly the package, the adopted structure and
conventions, as well as why they're adopted. 

> PS: These conventions where somewhat arbitrary
	  and reflect my lack of experience.

# Purpose

The variable star project developed since mission OP2018B-011 using the
B&C telescope on the OPD/LNA has generated large amounts of data. This
amount of data is too large for manual reduction using IRAF.

This package was developed out of the necessity of reduction facility
that took advantage of Python's flexibility, customized for the use on the
obtained data.

# Aim

To have a reduction pipeline capable of taking a folder from a night run
and do the following:
	
	- Organize FITS files (OK)
	- Create and apply calibration master files (bias and flat) (OK)
	- Align frames (OK)
	- Guide/help inspection process (Re-thinking)
	- Perform source detection (OK)
	- Combine final frames (OK)
	- Perform aperture photometry (OK?)
	- Generate light curve table (OK)
	
# Structure

The adopted structure was the one that appeared naturally when first 
playing with the idea for simplicity sake. 
(If necessary it can be reimplemented on the future)

To remove the necessity of writing an interface it was written to be used
with Python's console itself or trough a jupyter notebook just by calling
functions in a module called **processes**.

The structure of these functions is like of a main function in a simple
program. These "processes" where broken down into the smaller perceived
piece.  These pieces where implemented in smaller functions then these
"main" functions (on the processes module) where composed using it.

The smaller functions that works with images where made to work with only
one image at a time or as little as possible. This approach was taken to
make the scope of the functions itself handle the memory usage passively.

> PS: Was tested the use of image cubes. It was much faster but it added
a complication cause it required active memory handling (that i'm not
familiar with, so it was not adopted to expedite implementation).

These small functions are organized within sub-packages and modules

These processes functions can be used to composed into a single pipeline
script once everything is implemented with a small interface to the system
shell.

# Conventions

Conventions regarding the code, and the data formatting.

## Coding

The coding conventions where mainly taken straight from PEP 8. The linting 
program pycodestyle is used to support on the formatting of the modules.

## FITS Header

### Keywords

The header keys are the default ones from OPD. Some flags are added during the
reduction process to the generated files, usually to indicate process.

### Project conventions

The acquisition program on the observatory allows to enter some cards during 
observation runs. The conventions used are the ones adopted since mission 
OI2018B-011. Wich means:

    O: From OPD observatory
    I: On the IAG telescope
    2018B: In the period B of 2018,
    011: It was the 11th proposal

These conventions are used by the LNA folks to identify missions. So we use it
on the filename stems. Example:

    > OI2018B-011_2018-10-16_0001.fits

This filename means that, it is an image from that mission, the day was 16 of 
October, 2018, and it was the image number 1 of the night (starts on 0).

While doing calibration images we use the OBJECT keyword to signal which kind of
calibration is being done. Otherwise is used for what it is meant to. The program
expects this because it uses the object keyword separate calibration files. The
COMMENT keyword in this case is reserved to say what calibration apparatus was
used (Dome or Sky, Which lamp, etc).

The COMMENT keyword is used to signal the kind of frame. From the program point
of view it just tell if it is a science frame or another. If comment is science
it will calibrate the image.

    > NOTE: It's being studied the possibility of adding metadata to the folder 
    itself or using HDF5 to get faster performance and metadata support.

# Notebooks

The ideas were explored in notebooks first. They can work as documentation
since each step is described, and can be found at the notebooks folder.

> They will be added at the end of the exploration to not polute git history

# Warnings

- On the moment, this version of the package is only meant to test the idea the
  simplest perceived approach is taken in every step.

- This project is also a mean to learn about reduction and other subjects
  so a lot of decisions where taken just to maximize learning.
