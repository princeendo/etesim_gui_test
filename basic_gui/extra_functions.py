# -*- coding: utf-8 -*-

# AICET Imports
import data_input_objects as dio

# Module-Level Imports
import os
import platform
import re

# Aliased Module-Level Imports
import itertools as it
import pandas as pd
import tkinter as tk


####################################################################
# Utility functions
####################################################################
def absjoin(*args) -> str:
    """
    Performs os.path.join() on the arguments and then returns
    its absolute path

    Parameters
    ----------
    *args : iterable
        An iterable type of strings to be joined

    Returns
    -------
    str
        An os-specific path

    """
    return os.path.abspath(os.path.join(*args))


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


def assetGroups(assetTextList):
    """
    Reads a text list containing assets and separates them into
    a list of dictionaries where each dictionary contains the appropriate
    metadata for each asset.

    Parameters
    ----------
    assetTextList : list
        A list of strings where each element is a sequential line
        from a text file.

    Returns
    -------
    groups : list
        A list of dictionaries, each containing metadata for an asset.

    """
    groups = []
    k = 0
    n = len(assetTextList)
    while k < n:
        if assetTextList[k].lower() == '# asset':
            subGroup = {}
            j = k + 1
            while j < n and assetTextList[j].lower() != '# asset':
                _type, data = assetTextList[j].split(':')
                data = data.split()
                if len(data) == 1:
                    subGroup[_type] = data[0]
                else:
                    subGroup[_type] = data
                j += 1
            groups.append(subGroup)
            k = j
    return groups


def assetData(assetFile: str, simulation: str = 'etesim'):
    """
    A parser that performs the following:
        (1) Strips out all empty lines
        (2) Strips out leading/trailing whitespace and newline characters
        (3) Converts each remaining line to an element in a list

    Parameters
    ----------
    assetFile : str
        A file to parse
    simulation : str, optional
        A simulation specifier for "smart" splitting. The default is 'etesim'.

    Returns
    -------
    objs : TYPE
        DESCRIPTION.

    """
    with open(assetFile, 'r') as inFile:
        items = [x.strip() for x in inFile.readlines() if len(x.strip()) > 0]

    objs = []
    for asset in assetGroups(items):
        run_number = asset['Run']
        category = asset['Category']
        name = asset['Name']
        ID = asset['UniqueID']
        kwargs = {}
        if 'ECEF XYZ' in asset:
            kwargs['ecef'] = [float(x) for x in asset['ECEF XYZ']]
        if 'LatLonAlt' in asset:
            kwargs['lla'] = [float(x) for x in asset['LatLonAlt']]
        if 'ENU' in asset:
            kwargs['enu'] = [float(x) for x in asset['ENU']]
        objs.append(dio.FixedAsset(simulation, name, category, ID,
                                   run_number, **kwargs))
    return objs


def allAssets(dirlist, assetfileRegex: str = 'assets.txt',
              simulation: str = 'etesim'):
    """
    Finds files that represent assets in a given list of directories to search

    Parameters
    ----------
    dirlist : list
        A list of strings, each one representing a valid directory
    assetfileRegex : str, optional
        If any file in the dirlist matches this pattern, it is held.
        The default is 'assets.txt'.
    simulation : str, optional
        A simulation specifier for "smart" searching. The default is 'etesim'.

    Returns
    -------
    list
        A list of strings, each one a path to a file containing asset metadata

    """

    assetFiles = []
    matcher = re.compile(assetfileRegex)
    for dir_ in dirlist:
        for item in [x for x in os.scandir(dir_) if x.is_file()]:
            match = matcher.match(item.name)
            if match:
                assetFiles.append(item.path)

    assetLists = [assetData(f, simulation=simulation) for f in assetFiles]

    # Guarantees one long asset list
    return list(it.chain.from_iterable(assetLists))


def uniqueAssets(assetList):
    """
    Removes any duplicate assets from a list

    Parameters
    ----------
    assetList : list
        A list of assets.

    Returns
    -------
    assets : list
        A list of assets with duplicates removed.

    """
    assets = list(assetList)
    n = len(assets)
    k = n - 1
    while k >= 0 and n >= 0:
        asset = assets[k]
        j = k - 1
        while j >= 0:
            if assets[j] == asset:
                assets = assets[:k] + assets[k+1:]
                j = -1
                n = n - 1
            j = j - 1
        k = k - 1
    return assets


def assetsDF(assetList, unique: bool = False) -> pd.DataFrame:
    """
    Converts a list of FixedAsset type into a single DataFrame
    containing the relevant metadata

    Parameters
    ----------
    assetList : list
        A list of assets
    unique : bool, optional
        A flag for removing duplicate assets. The default is False.

    Returns
    -------
    Pandas DataFrame
        An indexed list of fixed assets.

    """

    # Converts the assets into DataFrames and indexes them in
    # the current order in the list
    df = pd.concat([x.df(k) for k, x in enumerate(assetList)])
    df.run = df.run.values.astype('int64')
    if unique:
        # This will not re-index to allow you to easily see what was dropped
        return df.drop_duplicates()
    else:
        return df


def assetColMap(colVal: tk.StringVar):
    """
    For a given user selection, lists the location the values of that
    selection should go in a DataFrame.

    Example: User selects 'Target Position - North' as a plotting region.
            That will map to being in the 'y' direction.

    Parameters
    ----------
    colVal : tk.StringVar
        A GUI variable that holds a string or a None.

    Returns
    -------
    str
        This is meant to be passed to a DataFrame. This lists the column
        in the DataFrame that the value will be mapped to for consistent
        plotting. Returns None if the value is invalid.

    """
    val = colVal.get()
    if val is None or val == '':
        return None
    splitData = val.lower().split()

    # assetType = splitData[0]
    loc = splitData[-1]

    if loc == 'east':
        return 'x'
    elif loc == 'north':
        return 'y'
    elif loc == 'up':
        return 'z'

    return None


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
    """
    Generates a DataFrame from an ETESim input and does some data
    extraction to add additional metadata columns.

    Parameters
    ----------
    inFile : str
        A path to the ETESim input file

    Returns
    -------
    df : Pandas DataFrame
        An indexed record of each time step of the output data

    """

    df = pd.read_excel(inFile).rename(columns=dictMap())
    model, instance = list(zip(*[recordExtractor(r, 'ETESim') for
                                 r in df['Data Record ID'].values]))
    df['Model'] = model
    df['Instance'] = instance
    df['Path'] = inFile
    return df
