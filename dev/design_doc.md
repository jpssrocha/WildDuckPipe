# Design Doc

Last update: 08-06-2020

This a simple doc describing quickly the package, the adopted structure and
conventions, as well as why they're adopted. 

> PS: These conventions where somewhat arbitrary
		and reflect my lack of experience.

# Purpose

The variable star project developed since mission OP2018B-011 using the
B&C telescope on the OPD/LNA has generated large amounts of data. This
amount of data was too large for manual reduction using IRAF.

This package was developed out of the necessity of reduction facility
that took advantage of Python's flexibility, customized for the use on the
obtained data.

# Aim

To have a reduction pipeline capable of taking a folder from a night run
and do the following:
	
	- Organize FITS files (OK)
	- Create and apply calibration master files (bias and flat) (OK)
	- Align frames (Reimplementing)
	- Perform source detection
	- Guide/help inspection process
	- Combine final frames (Reimplementing)
	- Perform aperture photometry
	- Generate light curve table
	
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

These small functions are organized within sub-packages and modules.

These processes functions can be used to composed into a single pipeline
script once everything is implemented with a small interface to the system
shell.

# Conventions

The coding conventions where mainly taken straight from PEP 8. The linting 
program pycodestyle is used to support on the formatting of the modules.

The language is varying between Portuguese and English, but it all will be
gradually put in English (will remove this paragraph when it happens)

# Warnings

- On the moment, this version of the package is only meant to test the idea the simplest perceived approach is taken in every step.

- This project is also a mean to learn about reduction and other subjects
so a lot of decisions where taken just to maximize learning.
