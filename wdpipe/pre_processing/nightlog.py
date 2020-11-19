"""
This module has tools to log the content of the FITS headers and create a summary
of the observed data.

Using it through the command line will create both the log file as well as a
summary file.

Basic usage:
------------
    
    $python nightlog.py <folder_name>


"""
import ccdproc
import pandas as pd
import os
from pathlib import Path

def get_log(folder, extra_keys=[], write=True):
    """
    Given a folder, it generate a log file with the listing of the keys given
    on the keys parameter. Default are the keys from OPD.

    Parameters
    ----------

    folder : String
        Path to the night run folder with the FITS files.

    extra_keys : List
        Listing of keys to look at in order, in addition to the default ones.

    write : bool
        If True writes an output csv (default is True)>

    Retuns
    ------

    log_tab: DataFrame
        Table containing information given on keys

    File transformations
    --------------------

    Write to disk a file named w/ the folder name + "_night.log" containing the 
    log inside the folder when write is True.

    """

    out = Path(folder)
    out = out / f"{str(out)}_night.log"


    keys = ["DATE-OBS", "OBJECT", "FILTER", 
            "EXPTIME", "AIRMASS", "COMMENT"]

    keys.extend(extra_keys)

    ifc = ccdproc.ImageFileCollection(folder, keywords=keys)
    
    df = ifc.summary.to_pandas(index="file")

    # Cleaning OPD comment and exptime. Then removing spaces from object.

    cleaners = {"COMMENT": lambda value: value.split("'")[1].strip(),
                "EXPTIME": lambda value: int(value.split(",")[0]),
                "OBJECT": lambda value: value.replace(" ", "")
                }

    for key in cleaners:
        df[key] = df[key].apply(cleaners[key])

    if write:
        df.to_csv(out)

    return [df, out]


def get_summary(table_file):
    """
    Given a log table create a summary in a human reable text file

    Parameters
    ----------

    table_file : pathlib.Path object
        Path to the log table.

    Retuns
    ------

    None

    File transformations
    --------------------

    Write text file w/ the table_file name + ".summary"

    """

    out = table_file
    out.rename(out.with_suffix(".summary"))


    
    #out = str(table_file).split(".")[0:-1] + ".summary"
    #out = Path(out)
    date = str(table_file).split("/")[0]


    # Load table
    table = pd.read_csv(table_file)

    # General info (total numbers, ranges)

    N = len(table)

    count = lambda tab, key, value: (tab[key] == value).sum()

    bias = count(table, "OBJECT", "bias")
    flat = count(table, "OBJECT", "flat")
    n_sci = count(table, "COMMENT", "science")

    calib = flat + bias
    others = N - bias - n_sci - flat

    def count_subset(tab, selection_key, value, counting_key):
        """
        Given a log table, take a subgroup that equals the value and count the
        components on the counting_key. Retuns a list of strings in exibition
        fashion.
        """
        counter_tab = (tab[tab[selection_key] == value][counting_key]).value_counts()

        strings = []
        strings.append("(  ")

        for val in counter_tab.index:
            strings.append(f"{val}: {counter_tab[val]}  ")
        strings.append(")")

        return strings

    flat_sub = count_subset(table, "OBJECT", "flat", "FILTER")

    # Science images

    sci = table[table["COMMENT"] == "science"]

    objs = sci.OBJECT.unique()

    def fmt_object(sci_tab, obj):
        """
        Given a table of science objects gives back formated information in 
        a string.
        """

        st = sci_tab[sci_tab.OBJECT == obj]
        n = len(st)
        exptimes = st.EXPTIME.unique()
        x_range = [str(st.AIRMASS.min())[:4], " < X < ", str(st.AIRMASS.max())[:4]]

        x_range = "".join(x_range)
        filters = "".join(count_subset(sci_tab, "OBJECT", obj, "FILTER"))

        out = [ f"\t{obj}: {n} {filters} \t Exptimes: {exptimes}s \t {x_range}" ]
    

        return "".join(out)

    
    # Generate text

    text = [ f"Summary {date}\n",
              "---------------\n\n",
              f"\tTotal: {N} \t Calibration: {calib} \t Science: {n_sci} \t Others: {others}\n",
               "\nCalibration files\n",
               "-----------------\n\n",
              f"\tBias images: {bias}\n",
              f"\tFlat images: {flat}\t"]

    text.extend(flat_sub)
    text.append("\n") 
    text.extend(["\nScience images\n",
                 "--------------\n\n"])

    for obj in objs:
        text.extend(fmt_object(sci, obj))
        text.append("\n")

    print("".join(text))

    with open(out, "w") as f:
        f.write("".join(text))

    return out


if __name__ == "__main__":
    import sys
    from pathlib import Path 
    
    folder_name = Path(sys.argv[1])

    _, file_name = get_log(folder_name)
    
    get_summary(file_name)

