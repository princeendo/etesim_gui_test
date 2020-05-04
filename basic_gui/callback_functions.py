# -*- coding: utf-8 -*-

import extra_functions as ef

import numpy as np
import os
import time
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import filedialog
import tkinter.colorchooser as tkColorChooser


def modifyLimitsEntry(gui, event: tk.Event, entry: str = None) -> None:
    """
    Modifies the Min/Max options for each variable (X/Y/Z) when the
    user clicks into or out of the field.

    If the field has Min (or Max) already in there, remove the
    text when the user enters the field.

    If the field has a non-float entry when the user leaves the field,
    restore Min (or Max) back to the field.

    Parameters
    ----------
    event : tk.Event
        Usually a focusIn or focusOut event which details whether
        the user has entered or left the field of interest
    entry : str, optional
        A metadescriptor which describes the location of where
        the user is or came from. The default is None.

    Returns
    -------
    None

    """
    focusIn = 9
    focusOut = 10
    evType = int(event.type._value_)

    # On focusIn events, if the value says Min or Max, delete it
    if evType == focusIn:
        if entry == 'xMin':
            if gui.xMinEntry.get() == 'Min':
                gui.xMinEntry.delete(0, tk.END)
        elif entry == 'xMax':
            if gui.xMaxEntry.get() == 'Max':
                gui.xMaxEntry.delete(0, tk.END)
        elif entry == 'yMin':
            if gui.yMinEntry.get() == 'Min':
                gui.yMinEntry.delete(0, tk.END)
        elif entry == 'yMax':
            if gui.yMaxEntry.get() == 'Max':
                gui.yMaxEntry.delete(0, tk.END)
        elif entry == 'zMin':
            if gui.zMinEntry.get() == 'Min':
                gui.zMinEntry.delete(0, tk.END)
        elif entry == 'zMax':
            if gui.zMaxEntry.get() == 'Max':
                gui.zMaxEntry.delete(0, tk.END)

    # On focusOut events, if the entry isn't a valid floating
    # point number, then put Min/Max back in where it should be
    elif evType == focusOut:
        if entry == 'xMin':
            try:
                float(gui.xMinEntry.get())
            except ValueError as ve:
                assert(ve)
                gui.xMinEntry.delete(0, tk.END)
                gui.xMinEntry.insert(0, 'Min')
        elif entry == 'xMax':
            try:
                float(gui.xMaxEntry.get())
            except ValueError as ve:
                assert(ve)
                gui.xMaxEntry.delete(0, tk.END)
                gui.xMaxEntry.insert(0, 'Max')
        elif entry == 'yMin':
            try:
                float(gui.yMinEntry.get())
            except ValueError as ve:
                assert(ve)
                gui.yMinEntry.delete(0, tk.END)
                gui.yMinEntry.insert(0, 'Min')
        elif entry == 'yMax':
            try:
                float(gui.yMaxEntry.get())
            except ValueError as ve:
                assert(ve)
                gui.yMaxEntry.delete(0, tk.END)
                gui.yMaxEntry.insert(0, 'Max')
        elif entry == 'zMin':
            try:
                float(gui.zMinEntry.get())
            except ValueError as ve:
                assert(ve)
                gui.zMinEntry.delete(0, tk.END)
                gui.zMinEntry.insert(0, 'Min')
        elif entry == 'zMax':
            try:
                float(gui.zMaxEntry.get())
            except ValueError as ve:
                assert(ve)
                gui.zMaxEntry.delete(0, tk.END)
                gui.zMaxEntry.insert(0, 'Max')


def editTitleOptions(gui, style: str = '') -> None:
    """
    Updates UI on whether user has pressed/unpressed the Bold Or Iatlic
    button and then has the plot title reflect that change.

    Parameters
    ----------
    style : str, optional
        A modifier parameter to indicate whether the bold or italic
        button has been pressed. The default is '' (for neither).

    Returns
    -------
    None

    """
    # Reading events
    if style == 'b':        # Swapping bold press state
        gui.boldTitleOn = not gui.boldTitleOn
    elif style == 'i':      # Swapping italic press state
        gui.itTitleOn = not gui.itTitleOn
    else:
        return              # Nothing to do

    # Swapping button behavior (pressed down or not)
    br = tk.SUNKEN if gui.boldTitleOn else tk.FLAT
    ir = tk.SUNKEN if gui.itTitleOn else tk.FLAT
    gui.boldTitleButton.config(relief=br)
    gui.itTitleButton.config(relief=ir)

    # Updating plot with new title style
    gui.startPlot(1)


def pickTitleColor(gui) -> None:
    """
    Takes the color chosen by the user from the colorwheel button
    and renders the title with that color.

    Returns
    -------
    None

    """
    # Takes color from user (None if exited without choosing color)
    # Returns a tuple of ((R, G, B), Hex)
    # R, G, B are floating point!
    color = tkColorChooser.askcolor(color=gui.titleColorRGB)
    if None not in color:
        # Sets the Hex value and updates the RGB value
        # The RGB value is used as the default in the colorchooser,
        # so that is why it needs to get set
        gui.titleColorHex.set(color[1])
        gui.titleColorRGB = ef.hex2rgb(gui.titleColorHex.get())
        editTitleOptions(gui, gui.titleColorHex.get())
    gui.startPlot(1)


def pickPlotColor(gui) -> None:
    """
    Takes the color chosen by the user from the colorwheel button
    and renders the plot with that color.

    Returns
    -------
    None

    """
    # Takes color from user (None if exited without choosing color)
    # Returns a tuple of ((R, G, B), Hex)
    # R, G, B are floating point!
    color = tkColorChooser.askcolor(color=gui.plotColorRGB)
    if None not in color:
        # Sets the Hex value and updates the RGB value
        # The RGB value is used as the default in the colorchooser,
        # so that is why it needs to get set
        gui.plotColorHex.set(color[1])
        gui.plotColorRGB = ef.hex2rgb(gui.plotColorHex.get())
        gui.startPlot(1)


def setLegendOptions(gui) -> None:
    """
    Enables or disables the combobox for legend locations based
    on whether the box is checked

    Returns
    -------
    None
        DESCRIPTION.

    """
    if gui.showLegend.get():
        gui.legendLocCB['state'] = 'readonly'
    else:
        gui.legendLocCB['state'] = 'disabled'

    gui.startPlot(1)


def setDimensions(gui) -> None:
    """
    Sets the dimensions for the plot based upon the columns
    selected by the user. If the user does not select both the
    x and y axis columns, then the dimensions are set to 0.
    If the user selects both x and y but not z, the dimension is 2.
    If the user selects x, y, and z, the dimension is 3

    Returns
    -------
    None

    """
    if gui.xCol.get() == '':       # x does not exist
        gui.dimensions = 0
        return
    elif gui.yCol.get() == '':     # x exists, y does not
        gui.dimensions = 0
        return
    elif gui.zCol.get() == '':     # x and y exist, z does not
        gui.dimensions = 2

        # Grid options exists on 2D graphs
        gui.gridMajorCB['state'] = 'normal'
        gui.gridMinorCB['state'] = 'normal'
    else:
        gui.dimensions = 3         # x, y, and z exist

        # 3D plots include a major grid by default
        # Minor grids in 3D introduce a bug
        gui.gridMinorCB['state'] = 'disabled'
        gui.gridMajorCB['state'] = 'disabled'

    # If any two columns match, there is no need to plot
    if (gui.xCol.get() == gui.yCol.get()
       or gui.xCol.get() == gui.zCol.get()
       or gui.yCol.get() == gui.zCol.get()):
        gui.dimensions = 0
        gui.status.set('Plot will not render if two elements match')


def setRunOptions(gui, event=None) -> None:
    """
    Sets the run numbers specified for looking at runs.
    Can enable/disable run number input based upon user selection.
    Will also set default values for the run number if there is
    an available set of run numbers to choose from

    Parameters
    ----------
    event : tk.Event, optional
        An event to be passed to turn this function into a handle.
        Not currently needed.
        The default is None.

    Returns
    -------
    None

    """

    # Set the ability for the user to edit the value based on choice
    newstate = 'disabled' if gui.showAllRuns.get() else 'normal'
    gui.runChoice['state'] = newstate
    gui.transRunsCB['state'] = newstate

    # Load the spinbox with the available choices if they exist
    if gui.availableRuns.size > 0:
        gui.runChoice['values'] = gui.availableRuns.tolist()

        # If there is no value in the box, set it
        if gui.runChoice.get() == '0':
            gui.runChoice.set(gui.availableRuns[0])
    else:
        gui.runChoice.set('')
        return

    # We need to do some value checking but will not be able to
    # if there are no values to choose from
    try:
        # if there is no entry for gui.run to select from, it
        # will be assigned an empty string and then try to do
        # type conversion. This will obviously fail.
        run = gui.run.get()
    except tk.TclError as tkTcl:
        assert(tkTcl)  # to shut linter up
        return

    # If a user-entered run number does not match any value in the
    # list of available runs, match it to the nearest value
    if isinstance(run, int) and run not in gui.availableRuns:
        diff_vals = np.abs(gui.availableRuns - run)
        nearest_idx = np.argmin(diff_vals)
        newval = gui.availableRuns[nearest_idx]
        gui.runChoice.set(newval)


def setVals(gui) -> None:
    """
    Checks whether user has selected X, Y, or Z columns from the
    ComboBox (drop-down) and sets the x, y, and z vectors from
    those choices.

    If both X and Y are not selected, nothing happens.
    If X and Y are selected but not Z, then a 2D plot will be rendered.
    If X, Y, and Z are selected, a 3D plot will be rendered.

    Returns
    -------
    None

    """

    # Guarantees dimensions are up to date
    setDimensions(gui)

    # If no dimensions, set values to nothing
    if gui.dimensions == 0:
        gui.x, gui.y, gui.z = [], [], []

    # If only 2D plot, only set x and y
    elif gui.dimensions == 2:
        gui.x = gui.missileDF[gui.xCol.get()].values
        gui.y = gui.missileDF[gui.yCol.get()].values

    # If 3D plot, set x, y, and z
    elif gui.dimensions == 3:
        gui.x = gui.missileDF[gui.xCol.get()].values
        gui.y = gui.missileDF[gui.yCol.get()].values
        gui.z = gui.missileDF[gui.zCol.get()].values
    return


def getTopDir(gui) -> None:
    """
    Opens a file browswer for the run files. Once selected,
    the chosen file path will show in the text field.
    The path can be typed in also.
    ** Only a directory can be selected

    Returns
    -------
    None

    """

    kwargs = {'title': 'Select Directory Containing Run(s)',
              'mustexist': True, }

    # If you have not selected a path, set up a default path
    # If something is already set, the file dialog should default there
    if gui.topDir == '':
        kwargs['initialdir'] = ef.default_path()
    else:
        kwargs['initialdir'] = gui.topDir

    selection = filedialog.askdirectory(**kwargs)
    if selection != '':
        gui.topDir = os.path.abspath(selection)

    # Updates text widget with path (deletes old path)
    gui.topDirPath.delete('1.0', tk.END)
    gui.topDirPath.insert(1.0, gui.topDir)


def loadFromTopDir(gui) -> None:
    """
    Loads missile file from topDir, if possible.
    If directory is invalid, display a warning message.
    If missile file loads successfully, update status.

    Returns
    -------
    None

    """
    # If the entry is not a valid directory, display a warning message
    if not os.path.isdir(gui.topDir):
        gui.status.set('No file(s) loaded')
        mb.showinfo('Invalid directory',                 # title
                    'Please choose a valid directory!',  # message
                    icon='warning',)
        return

    # This should already be true, but setting just in case
    gui.topDir = os.path.abspath(gui.topDir)
    loadMissileFiles(gui)


def loadMissileFiles(gui, write_csv=True) -> str:
    """
    Checks for whether 'NotionalETEOutput###.xlsx' is present in topDir.
    (The ### is a random number between 000 and 999, always three digits)
    If present, loads the missile file into a dataframe, updates the
    dataframe columns, and makes available for plotting only the
    dataframe columns that have floating-point data

    ** Will definitely need to be updated upon porting

    Returns
    -------
    str
        The absolute path to the missile file

    """
    gui.status.set(f'Searching {gui.topDir} for files')  # updating user

    # Looking for files to read in directory
    tree = ef.dirTree(gui.topDir)
    missileFiles = ef.allMissileFiles(tree)

    # Counting time for process to occur
    startTime = time.time()

    # Making massive DataFrame of all the missile files in tree
    N = len(missileFiles)
    gui.status.set(f'Loading {N} file' + 's' * (N > 1))
    gui.missileDF = ef.combinedMissleDF(missileFiles)
    gui.missileDF.rename(columns=ef.dictMap(), inplace=True)
    gui.missileDF.sort_values(by=['Time', 'RunNumber'], inplace=True)

    # Updating user on the operation and its total time
    totalTime = int(time.time() - startTime)
    newStatus = f'Loaded {N} file' + 's' * (N > 1) + f' in {totalTime}s'
    gui.status.set(newStatus)

    # Determining available runs based upon unique IDs
    if 'RunNumber' in gui.missileDF.columns:
        gui.availableRuns = gui.missileDF.RunNumber.unique()
        setRunOptions(gui)
        gui.run.set(gui.availableRuns[0])

    # Takes the columns from the DataFrame and makes them available
    # to be plotted on any axis. The first entry will be blank
    # so that users must choose to plot
    gui.plotCols = [''] + sorted([col for col, val
                                  in gui.missileDF.dtypes.items()
                                  if val == np.dtype('float64')])
    gui.xCB['values'] = gui.plotCols
    gui.yCB['values'] = gui.plotCols
    gui.zCB['values'] = gui.plotCols

    outFile = os.path.join(gui.topDir, 'out.csv')
    if write_csv:
        gui.missileDF.to_csv(outFile, index=False)
    return outFile


def setStatusBarOptions(gui, event=None) -> None:
    """
    Updates the the elements displayed in the status bar.

    Parameters
    ----------
    event : tk.Event, optional
        An event that can drive the call. The default is None.

    Returns
    -------
    None

    """

    # Capturing current tab
    tab = gui.tabs.index(gui.tabs.select())

    if tab == 0:  # Data Input Tab
        gui.xkcdModeCB.pack_forget()
    elif tab == 1:  # Viewer Tab
        gui.xkcdModeCB.pack(fill=tk.BOTH, side=tk.RIGHT)
    else:
        gui.status.set(f'You are on tab {tab} which must be new')


def setPlotStyleOptions(gui) -> None:
    """
    Checks whether the radio button for 'line' or 'scatter' is selected.
    For the selected option, it makes the ComboBox (drop-down)
    active and selectable by the user

    Returns
    -------
    None

    """
    if gui.plotStyle.get() == 'line':
        gui.lineStyleCB.config(state='readonly')
        gui.scatterStyleCB.config(state='disabled')
    if gui.plotStyle.get() == 'scatter':
        gui.lineStyleCB.config(state='disabled')
        gui.scatterStyleCB.config(state='readonly')
    gui.startPlot('update')  # Need a non-None event


def showHidePlotColors(gui) -> None:
    """
    Changes the ability to interact with the plotColor entry and button
    elements based upon whether autoColor has been selected

    Returns
    -------
    None

    """

    # Disables the ability to edit if the autocolor option is set
    # Otherwise, restores it to normal
    newstate = 'disabled' if gui.autoColor.get() else 'normal'
    gui.plotColorEntry['state'] = newstate
    gui.plotColorButton['state'] = newstate

    # Updates plot based on choice
    gui.startPlot(1)


def showHideXLimits(gui) -> None:
    """
    Determines whether or not to display the boxes for setting
    the minimum and maximum limits for the X variable.
    Checks the status of the tk.CheckBox in the GUI to determine
    behavior

    Returns
    -------
    None

    """
    if gui.xLimits.get():  # if checked, show entry fields
        gui.xMinEntry.grid(row=gui.xLimitsRow, column=2)
        gui.xMaxEntry.grid(row=gui.xLimitsRow, column=3)
    else:                   # hide fields
        gui.xMinEntry.grid_remove()
        gui.xMaxEntry.grid_remove()
    gui.startPlot(1)


def showHideYLimits(gui) -> None:
    """
    Determines whether or not to display the boxes for setting
    the minimum and maximum limits for the Y variable.
    Checks the status of the tk.CheckBox in the GUI to determine
    behavior

    Returns
    -------
    None

    """
    if gui.yLimits.get():  # if checked, show entry fields
        gui.yMinEntry.grid(row=gui.yLimitsRow, column=2)
        gui.yMaxEntry.grid(row=gui.yLimitsRow, column=3)
    else:                   # hide fields
        gui.yMinEntry.grid_remove()
        gui.yMaxEntry.grid_remove()
    gui.startPlot(1)


def showHideZLimits(gui) -> None:
    """
    Determines whether or not to display the boxes for setting
    the minimum and maximum limits for the Z variable.
    Checks the status of the tk.CheckBox in the GUI to determine
    behavior

    Returns
    -------
    None

    """
    if gui.zLimits.get():  # if checked, show entry fields
        gui.zMinEntry.grid(row=gui.zLimitsRow, column=2)
        gui.zMaxEntry.grid(row=gui.zLimitsRow, column=3)
    else:                   # hide fields
        gui.zMinEntry.grid_remove()
        gui.zMaxEntry.grid_remove()
    gui.startPlot(1)
