# -*- coding: utf-8 -*-

# Module-Level Imports
import os
import platform
import re

# Aliased Module-Level Imports
import pandas as pd
import tkinter as tk


####################################################################
# Utility functions
####################################################################
def hex2rgb(hexstring: str) -> tuple:
    """
    A method to convert 6-digit hexadecimal values to a triplet
    of values in the range (0-255)

    Parameters
    ----------
    hexstring : str
        A hex color string in the form #XXXXXX, where each X is
        a hexadecimal number

    Returns
    -------
    tuple
        A triplet of the form (A, B, C) where A, B, and C are integers
        between 0 and 255 (inclusive)

    """
    rgb = []
    for i in range(3):
        # The first element of the string is '#'
        # Each section of two digits is sliced off
        string_ = hexstring[1 + 2 * i:1 + 2 * (i + 1)]

        # Converts the hex value to an integer in [0, 255]
        rgb.append(int(f'0x0000{string_}', 0))
    return tuple(rgb)


def default_path() -> str:
    """
    Gives an OS-specific default path to display in filedialog windows.

    Returns
    -------
    str
        'C:' for Windows, '/' for Unix, '//' for Linux
        Not currently defined for other operating systems

    """
    defaultPaths = {'windows': 'C:\\',
                    'unix': '/',
                    'linux': '//',
                    'macos': None,
                    'sunos': None,
                    }
    thisOS = platform.system().lower()
    return defaultPaths[thisOS]


####################################################################
# Item Renamers
####################################################################
def dictMap():
    """
    A mapper to take columns from the input file and generate
    meaningful, human-readable columns. Intended to be used
    with the .rename() function for a dataframe.

    Returns
    -------
    dMap : dict
        A mapping str->str intended to be used for dataframes

    """
    dMap = {
        'uniqueid': 'RunNumber',
        'datatype': 'Data Type',
        'datarec_id': 'Data Record ID',
        'header_swmodel': 'Model',
        'time': 'Time',
        'mEast': 'Missile Position - East',
        'mNorth': 'Missile Position - North',
        'mUp': 'Missile Position - Up',
        'tEast': 'Target Position - East',
        'tNorth': 'Target Position - North',
        'tUp': 'Target Position - Up',
        }
    return dMap


def recordExtractor(datarecID: str, sim: str = 'ETESim') -> tuple:
    """
    Extracts metadata from sim data records to get meaningful strings.

    The user will be able to get a record of the form (<Model>, <Instance>)

    Parameters
    ----------
    datarecID: str
        A string for which metadata will be extracted

    sim : str, optional
        The simulation from which data extraction will occur
        The default is 'ETESim'.

    Returns
    -------
    tuple
        An ordered pair of strings which contain the model and instance

    """

    # Hopefully this will grow over time
    available_sims = ('ETESim')

    # If the sim is not supported, do nothing to the string
    if sim not in available_sims:
        return datarecID

    # Elements of the form
    # <Object>_<Type>_<Instance>.<Object>_<Type>.<Instance>
    # Example: MISSILE_SAMP7_1.MISSILE_SAMP7.1
    if sim == 'ETESim':
        regex = r'[A-Z]+_([A-Z]+\d*)_(\d+)\..*'
        q = re.compile(regex)
        mo = q.match(datarecID)

        # Returns "<Model>, <Instance>" as a tuple
        return mo.groups()


####################################################################
# Directory parsing functions
####################################################################
def dirTree(root: str) -> list:
    """
    Generates a list containing a directory and all its subdirectories.

    Parameters
    ----------
    root : str
        A top-level directory to traverse.

    Returns
    -------
    list
        The directory and all subdirectories.

    """
    # Scan directory and keep only subdirectories
    subdirs = [x.path for x in os.scandir(root) if x.is_dir()]

    # Recursively call dirtree() on the subdirectories
    subtree = [dirTree(x) for x in subdirs]

    # Building a list of all the items in the subdirectories
    tree = [root]
    for list_ in subtree:    # Each element in the subtree is a list
        for dir_ in list_:
            tree.append(dir_)
    return tree


def allMissileFiles(
        dirlist: list,
        mfile_regex: str = 'NotionalETEOutput(\\d+).xlsx') -> list:
    """
    Generates a list of files from the supplied directory list
    which match the specified pattern.

    Parameters
    ----------
    dirlist : list
        A list of directories to check for files
    mfile_regex : str, optional
        The matching criterion (regular expression).
        The default is 'NotionalETEOutput(\\d+).xlsx'.

    Returns
    -------
    list
        The path for each file matching the criterion.

    """

    missileFiles = []
    for dir_ in dirlist:
        for item in os.scandir(dir_):
            if item.is_file():
                check = re.match(mfile_regex, item.name)
                if check is not None:
                    missileFiles.append(item.path)
    return missileFiles


def combinedMissleDF(missileFileList: list) -> pd.DataFrame:
    """
    Combines a list of input files into a single DataFrame by
    generating a single DataFrame for each file and using the
    concatenation function to generate a single object.

    Transforms Path and uniqueID into categorical variables because
    it's going to have a lot of repeats

    Parameters
    ----------
    missileFileList : list
        The path to each file to be combined into the DataFrame

    Returns
    -------
    pd.DataFrame
        A Pandas DataFrame of the combined object

    """
    df = pd.concat(map(makeDF, missileFileList))
    return df


def makeDataFrameAddPath(inFile: str) -> pd.DataFrame:
    """
    Makes a DataFrame from an Excel file and adds the path
    of the file as a new column

    Parameters
    ----------
    inFile : str
        An Excel spreadsheet that has panel data

    Returns
    -------
    df : pd.DataFrame
        A Pandas DataFrame of the data with one additional column added

    """
    df = pd.read_excel(inFile)
    df['Path'] = inFile
    return df


def makeDF(inFile: str) -> pd.DataFrame:

    df = pd.read_excel(inFile).rename(columns=dictMap())
    model, instance = list(zip(*[recordExtractor(r, 'ETESim') for
                                 r in df['Data Record ID'].values]))
    df['Model'] = model
    df['Instance'] = instance
    df['Path'] = inFile
    return df


def seabornDF(gui, plotDF):
    
    # To do seaborn plots, we will need to interpolate each item to get
    # a common x-axis between plots. If we do not do this, the banding
    # part of the line plot won't be helpful

    # Editing the status bar to present new information
    # self.statusLbl.pack_forget()
    gui.status.hide()
    gui.plotProgressFrame.pack(fill=tk.BOTH, side=tk.LEFT)
    numDFs = sum([1 for (_, df) in plotDF.groupby(keepCols)])
    newDFs = []

    xVals = plotDF.x.values[0:plotDF.shape[0]:numDFs]
    for k, (meta, subdf) in enumerate(plotDF.groupby(keepCols)):
        yVals = np.interp(xVals, subdf.x, subdf.y)
        d = {'x': xVals, 'y': yVals}
        if gui.dimensions == 3:
            zVals = np.interp(xVals, subdf.x, subdf.z)
            d['z'] = zVals
        for idx, item in enumerate(keepCols):
            d[item] = [meta[idx]] * len(yVals)
        newDFs.append(pd.DataFrame(d))

        # This keeps the matplotlib process from blocking updates
        gui.canvas.draw()
        gui.plotProgress.set(100*(k+1)/(numDFs))
        gui.plotProgressLbl.set(f'{k+1}/{numDFs} complete')

    newDF = pd.concat(newDFs)

    # Removing the counter and setting status back to normal
    gui.plotProgressFrame.pack_forget()
    gui.status.show(f'Size grew from {plotDF.shape[0]} to {newDF.shape[0]}')
    gui.canvas.draw()

    return newDF