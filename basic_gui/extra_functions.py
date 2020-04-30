# -*- coding: utf-8 -*-

# Module-Level Imports
import os
import platform
import re

# Aliased Module-Level Imports
import pandas as pd


####################################################################
# Utility functions
####################################################################
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
