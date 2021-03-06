# -*- coding: utf-8 -*-

import callback_functions as cf
import extra_functions as ef

# Module-level imports
import os

# Tkinter imports
import tkinter as tk
import tkinter.font as font
from tkinter import ttk


class guiTextLabel():
    def __init__(gui: tk.Tk, parent: tk.Frame, style: str, **kwargs) -> None:
        """
        An all-in-one class designed to create a label and place it in the
        GUI without having to write a large portion of commands.

        Parameters
        ----------
        gui : tk.Tk
            A tkinter GUI
        parent : tk.Frame
            The parent for the label
        style : str
            Options are 'pack' or 'grid' to specify tkinter method for display
        **kwargs : dict
            Keyword arguments for the label options and the display options

        Returns
        -------
        None

        """

        gui.text = tk.StringVar(parent, '')

        # Takes the keyword arguments passed and splits them into
        # the ones related to the label and the ones related to
        # packing/gridding the label
        gui.labelKwargs, gui.showKwargs = splitKwargs(**kwargs)

        gui.label = tk.Label(parent, **gui.labelKwargs,
                             textvariable=gui.text)

        if 'text' in gui.labelKwargs:
            gui.text.set(gui.labelKwargs['text'])

        gui.show = gui._pack if style == 'pack' else gui._grid
        gui.hide = gui._pack_forget if style == 'pack' else gui._grid_forget

    def _pack(gui: tk.Tk, text: str = None) -> None:
        """
        Places the label in the GUI using the pack() method.

        Parameters
        ----------
        gui : tk.Tk
            A tkinter GUI
        text : str, optional
            The text to display in the label. The default is None.

        Returns
        -------
        None

        """
        notText = {k: v for (k, v) in gui.showKwargs.items() if k != 'text'}

        gui.label.pack(**notText)
        if text is not None:
            gui.set(text)
        elif 'text' in gui.labelKwargs:
            gui.set(gui.labelKwargs['text'])

    def _pack_forget(gui: tk.Tk) -> None:
        """
        Hides the label in the GUI.

        Parameters
        ----------
        gui : tk.Tk
            A tkinter GUI

        Returns
        -------
        None

        """
        gui.label.pack_forget()

    def _grid(gui: tk.Tk, text: str = None) -> None:
        """
        Places the label in the GUI using the grid() method.

        Parameters
        ----------
        gui : tk.Tk
            A tkinter GUI
        text : str, optional
            The text to display in the label. The default is None.

        Returns
        -------
        None

        """
        gui.label.grid(**gui.showKwargs)
        if text is not None:
            gui.set(text)

    def _grid_forgt(gui: tk.Tk) -> None:
        """
        Hides the label in the GUI.

        Parameters
        ----------
        gui : tk.Tk
            A tkinter GUI

        Returns
        -------
        None

        """
        gui.label.grid_forget()

    def set(gui: tk.Tk, newText: str) -> None:
        """
        Sets the text value for the label

        Parameters
        ----------
        gui : tk.Tk
            A tkinter GUI
        newText : str
            The new value for the label

        Returns
        -------
        None

        """
        gui.text.set(newText)

    def get(gui,) -> str:
        """
        Gets the current value of the label

        Parameters
        ----------
        gui : tk.Tk
            A tkinter GUI

        Returns
        -------
        str
            The value of the label.

        """
        return gui.text.get()


def splitKwargs(**kwargs):
    """
    Allows a user to pass a single keyword argument dictionary when creating
    a label and "smartly" splits the keywords into the keywords needed
    for creating labels and for packing or gridding the label.

    Parameters
    ----------
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    labelArgs : TYPE
        DESCRIPTION.
    showArgs : TYPE
        DESCRIPTION.

    """
    labelOpts = {'anchor', 'bg', 'bitmap', 'bd', 'cursor', 'font', 'fg',
                 'height', 'image', 'justify', 'relief', 'text',
                 'textvariable', 'underline', 'width', 'wraplength'}

    packOpts = {'expand', 'fill', 'side'}

    gridOpts = {'column', 'columnspan', 'ipadx', 'ipady', 'padx', 'pady',
                'row', 'rowspan', 'sticky'}

    labelArgs = {}
    showArgs = {}

    for key, value in kwargs.items():
        if key in labelOpts:
            labelArgs[key] = value
        elif key in packOpts.union(gridOpts):
            showArgs[key] = value

    return labelArgs, showArgs


def buildXYZFieldSelectors(parent, values, plotFunc):
    """
    Builds the elements for selecting which columns to plot from input data

    Parameters
    ----------
    parent : tk.Frame
        The holder of these field selectors
    values : list
        The options that will be placed in each ComboBox
    plotFunc : function pointer
        The plotting function for the GUI

    Returns
    -------
    axData : list
        The handles to each of the field selectors made in this function

    """
    # Setting identical data for XYZ ComboBoxes
    comboKwargs = {'values': values, 'state': 'readonly', 'width': 30}

    # Builds three label/combobox combinations where the layout is
    # X= [                       |v|]
    # Y= [                       |v|]
    # Z= [                       |v|]
    # Each of the above is a dropdown menu
    axData = [buildFieldSelector(parent, row, ax, plotFunc, **comboKwargs)
              for row, ax in enumerate(['X', 'Y', 'Z'])]
    return axData


def buildFieldSelector(parent, row, axis, plotFunc, **comboKwargs):
    """
    Builds the elements needed to select a parameter for plotting along
    a specified axis.

    Examples might be on row 0 for axis 'X'.
    The keyword arguments are passed instead of specified here

    Parameters
    ----------
    parent : tk.Frame
        The holder of this field selector
    row : int
        The row to place the field selector upon inside the parent.
        Intended for stacking vertically.
    axis : str
        Can be anything, but intended for "X", "Y", or "Z"
    plotFunc : function pointer
        The plotting function for the GUI
    **comboKwargs : dict
        Keyword arguments for the ComboBox

    Returns
    -------
    axCol : tk.StringVar
        The handle to the value selected in the ComboBox that is built
    cb : TYPE
        The handle to the ComboBox that is built

    """
    labelKwargs = {'row': row, 'column': 0, 'sticky': tk.W, 'padx': (2, 0), }

    axCol = tk.StringVar()
    label = tk.Label(parent, text=f'{axis}=')
    label.grid(**labelKwargs)
    cb = ttk.Combobox(parent, textvariable=axCol, **comboKwargs)
    cb.grid(row=row, column=1)
    cb.bind('<<ComboboxSelected>>', plotFunc)
    return (axCol, cb)


def buildXYZMinMaxModifiers(gui: tk.Tk, parent: tk.Frame, waitFunc) -> None:
    """
    Adds elements for modifying the limits for X, Y, and Z values

    Parameters
    ----------
    gui : tk.Tk
        A tkinter GUI
    parent : tk.Frame
        A placeholder for all of these elements
    waitFunc : function
        A function pointer for having the GUI wait before acting

    Returns
    -------
    None

    """

    limitskwargs = {'width': 8, 'validate': "key"}

    # - - - - - - - - - -
    # Row 0 - X Min/Max
    gui.xLimitsRow = 0
    gui.xLimits = tk.BooleanVar(value=False)

    # Checkbox for turning on limit setting
    gui.xLimitsBox = tk.Checkbutton(
                            parent,
                            text='X ',
                            variable=gui.xLimits,
                            command=lambda: cf.showHideXLimits(gui))
    gui.xLimitsBox.grid(row=gui.xLimitsRow, column=0, sticky=tk.W)

    # Entry for minimum Y value
    gui.xMin = tk.StringVar()
    gui.xMinEntry = tk.Entry(parent, **limitskwargs)
    gui.xMinEntry['textvariable'] = gui.xMin
    gui.xMinEntry.insert(0, 'Min')
    gui.xMinEntry.bind('<Key>', waitFunc)
    gui.xMinEntry.bind("<FocusIn>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'xMin'))
    gui.xMinEntry.bind("<FocusOut>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'xMin'))

    # Entry for maximum Y value
    gui.xMax = tk.StringVar()
    gui.xMaxEntry = tk.Entry(parent, **limitskwargs)
    gui.xMaxEntry['textvariable'] = gui.xMax
    gui.xMaxEntry.insert(0, 'Max')
    gui.xMaxEntry.bind('<Key>', waitFunc)
    gui.xMaxEntry.bind("<FocusIn>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'xMax'))
    gui.xMaxEntry.bind("<FocusOut>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'xMax'))

    # - - - - - - - - - -
    # Row 1 - Y Min/Max
    gui.yLimitsRow = 1
    gui.yLimits = tk.BooleanVar(value=False)

    # Checkbox for turning on limit setting
    gui.yLimitsBox = tk.Checkbutton(
                            parent,
                            text='Y ',
                            variable=gui.yLimits,
                            command=lambda: cf.showHideYLimits(gui))
    gui.yLimitsBox.grid(row=gui.yLimitsRow, column=0, sticky=tk.W)

    # Entry for minimum Y value
    gui.yMin = tk.StringVar()
    gui.yMinEntry = tk.Entry(parent, **limitskwargs)
    gui.yMinEntry['textvariable'] = gui.yMin
    gui.yMinEntry.insert(0, 'Min')
    gui.yMinEntry.bind('<Key>', waitFunc)
    gui.yMinEntry.bind("<FocusIn>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'yMin'))
    gui.yMinEntry.bind("<FocusOut>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'yMin'))

    # Entry for maximum Y value
    gui.yMax = tk.StringVar()
    gui.yMaxEntry = tk.Entry(parent, **limitskwargs)
    gui.yMaxEntry['textvariable'] = gui.yMax
    gui.yMaxEntry.insert(0, 'Max')
    gui.yMaxEntry.bind('<Key>', waitFunc)
    gui.yMaxEntry.bind("<FocusOut>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'yMax'))
    gui.yMaxEntry.bind("<FocusIn>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'yMax'))

    # - - - - - - - - - -
    # Row 2 - Z Min/Max
    gui.zLimitsRow = 2
    gui.zLimits = tk.BooleanVar(value=False)

    # Checkbox for turning on limit setting
    gui.zLimitsBox = tk.Checkbutton(
                            parent,
                            text='Z ',
                            variable=gui.zLimits,
                            command=lambda: cf.showHideZLimits(gui))
    gui.zLimitsBox.grid(row=gui.zLimitsRow, column=0, sticky=tk.W)

    # Entry for minimum Z value
    gui.zMin = tk.StringVar()
    gui.zMinEntry = tk.Entry(parent, **limitskwargs)
    gui.zMinEntry['textvariable'] = gui.zMin
    gui.zMinEntry.insert(0, 'Min')
    gui.zMinEntry.bind('<Key>', waitFunc)
    gui.zMinEntry.bind("<FocusIn>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'zMin'))
    gui.zMinEntry.bind("<FocusOut>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'zMin'))

    # Entry for maximum Z value
    gui.zMax = tk.StringVar()
    gui.zMaxEntry = tk.Entry(parent, **limitskwargs)
    gui.zMaxEntry['textvariable'] = gui.zMax
    gui.zMaxEntry.insert(0, 'Max')
    gui.zMaxEntry.bind('<Key>', waitFunc)
    gui.zMaxEntry.bind("<FocusIn>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'zMax'))
    gui.zMaxEntry.bind("<FocusOut>",
                       lambda _: cf.modifyLimitsEntry(gui, _, 'zMax'))


def buildCustomTitleOptions(gui: tk.Tk, parent: tk.Frame,
                            waitFunc, startPlotFunc, ) -> None:
    """
    Adds elements for creating a custom title

    Parameters
    ----------
    gui : tk.Tk
        A tkinter GUI
    parent : tk.Frame
        A placeholder for all of these elements
    waitFunc : function
        A function pointer for having the GUI wait before acting
    startPlotFunc : function
        Kicks off the plot in the viewer pane

    Returns
    -------
    None

    """

    # - - - - - - - - - -
    # Row 0 - Text
    gui.titleText = tk.StringVar()
    titlekwargs = {'width': 35, 'textvariable': gui.titleText, }
    gui.titleEntry = ttk.Entry(parent, **titlekwargs)
    gui.titleEntry.insert(0, '')

    # Adds a waiting period for the user to stop typing
    gui.titleEntry.bind('<Key>', waitFunc)
    gui.titleEntry.grid(row=0, column=0, sticky=tk.W, columnspan=5)

    # - - - - - - - - - -
    # Row 1 - Styling
    gui.titleSize = ttk.Spinbox(parent, from_=0, to=32, width=3,
                                command=lambda: startPlotFunc(1))
    gui.titleSize.set('15')
    gui.titleSize.grid(row=1, column=0)

    gui.boldTitleOn, gui.itTitleOn = (0, 0)

    # Bold button
    boldFont = font.Font(size=10, weight="bold")
    gui.boldTitleButton = tk.Button(
                            parent, text="B", width=3,
                            relief=tk.FLAT,
                            font=boldFont,
                            command=lambda: cf.editTitleOptions(gui, 'b'))
    gui.boldTitleButton.grid(row=1, column=1,)

    # Italic button
    itFont = font.Font(size=10, slant="italic")
    gui.itTitleButton = tk.Button(
                            parent, text="I", width=3,
                            relief=tk.FLAT,
                            font=itFont,
                            command=lambda: cf.editTitleOptions(gui, 'i'))
    gui.itTitleButton.grid(row=1, column=2,)

    # Title Color Picker
    tc_kwargs = {'width': 8, 'textvariable': gui.titleColorHex, }
    gui.titleColorEntry = ttk.Entry(parent, **tc_kwargs)

    # Adds a waiting period for the user to stop typing
    gui.titleColorEntry.bind('<Key>', waitFunc)
    gui.titleColorEntry.grid(row=1, column=3, sticky=tk.W)

    # Setting up color wheel buttong
    gui.titleColorWheel = tk.PhotoImage(file='images/color_wheel.png')
    gui.titleColorButton = tk.Button(
                                parent,
                                image=gui.titleColorWheel,
                                command=lambda: cf.pickTitleColor(gui))
    gui.titleColorButton.grid(row=1, column=4,)


def buildStyleOptions(gui: tk.Tk, parent: tk.Frame,
                      waitFunc, startPlotFunc, ) -> None:
    """
    Adds style options for the graph
        Line/Scatter plot selector
        Line/Scatter plot options
        Legend display
        Legend location
        Autocoloring of line/scatter plots
        Selective coloring of line/scatter plots

    Parameters
    ----------
    gui : tk.Tk
        A tkinter GUI
    parent : tk.Frame
        A placeholder for all of these elements
    waitFunc : function
        A function pointer for having the GUI wait before acting
    startPlotFunc : function
        Kicks off the plot in the viewer pane

    Returns
    -------
    None

    """

    # - - - - - - - - - -
    # Row 0 - Plot/Scatter
    gui.plotStyle = tk.StringVar(parent, 'line')

    linekwargs = {'text': 'Line', 'var': gui.plotStyle, 'value': 'line',
                  'command': lambda: cf.setPlotStyleOptions(gui, ), }

    scatterkwargs = {'text': 'Scatter', 'var': gui.plotStyle,
                     'value': 'scatter',
                     'command': lambda: cf.setPlotStyleOptions(gui, ), }

    gui.lineOn = ttk.Radiobutton(parent, **linekwargs,)
    gui.scatterOn = ttk.Radiobutton(parent, **scatterkwargs)

    # Setting up a CB to be placed beside Line Style radio button
    gui.lineStyleOptions = ('-', '--', ':', '-.', )
    gui.lineStyle = tk.StringVar(parent, '-')
    lineStyle_kwargs = {'textvariable': gui.lineStyle,
                        'values': gui.lineStyleOptions,
                        'state': 'readonly',
                        'width': 4}
    gui.lineStyleCB = ttk.Combobox(parent, **lineStyle_kwargs)

    # Setting up a CB to be placed beside Scatter Style radio button
    gui.scatterStyleOptions = ('o', 'v', '^', '<', '>', '8', 's', 'p',
                               '*', 'h', 'H', 'D', 'd', 'P', 'X')
    gui.scatterStyle = tk.StringVar(parent, 'o')

    scatterStyle_kwargs = {'textvariable': gui.scatterStyle,
                           'values': gui.scatterStyleOptions,
                           'state': 'disabled',
                           'width': 4}

    gui.scatterStyleCB = ttk.Combobox(parent, **scatterStyle_kwargs)

    gui.lineOn.grid(row=0, column=0, padx=(0, 0))
    gui.lineStyleCB.grid(row=0, column=1)
    gui.lineStyleCB.bind('<<ComboboxSelected>>', startPlotFunc)
    gui.scatterOn.grid(row=0, column=2, padx=(10, 0))
    gui.scatterStyleCB.grid(row=0, column=3)
    gui.scatterStyleCB.bind('<<ComboboxSelected>>', startPlotFunc)

    # - - - - - - - - - -
    # Row 1 - Legend
    gui.showLegend = tk.BooleanVar(value=True)
    gui.legendLoc = tk.StringVar(parent, value='Best')

    legendCB_kwargs = {'text': 'Show Legend', 'variable': gui.showLegend,
                       'command': lambda: cf.setLegendOptions(gui,), }
    gui.legendCB = tk.Checkbutton(parent, **legendCB_kwargs)
    gui.legendCB.grid(row=1, column=0, columnspan=2, sticky=tk.W)

    gui.legendLocations = ('Best', 'Outside Right')
    legendLoc_kwargs = {'textvariable': gui.legendLoc,
                        'values': gui.legendLocations,
                        'state': 'readonly',
                        'width': 14}
    gui.legendLocCB = ttk.Combobox(parent, **legendLoc_kwargs)
    gui.legendLocCB.grid(row=1, column=2, columnspan=2, sticky=tk.E)
    gui.legendLocCB.bind('<<ComboboxSelected>>', startPlotFunc)

    # - - - - - - - - - -
    # Row 2 - Plot Color

    # Setting up whether the colors should be made automatically
    gui.autoColor = tk.BooleanVar(value=True)
    ac_kwargs = {'text': 'Auto Color', 'variable': gui.autoColor,
                 'command': lambda: cf.showHidePlotColors(gui, ), }
    gui.autoColorCB = tk.Checkbutton(parent, **ac_kwargs)
    gui.autoColorCB.grid(row=2, column=0, columnspan=2, sticky=tk.W)

    # Plot Color Picker
    pc_kwargs = {'width': 10, 'textvariable': gui.plotColorHex,
                 'state': 'disabled', }
    gui.plotColorEntry = ttk.Entry(parent, **pc_kwargs)

    # Adds a waiting period for the user to stop typing
    gui.plotColorEntry.bind('<Key>', waitFunc)
    gui.plotColorEntry.grid(row=2, column=2, sticky=tk.E, pady=0)

    # Setting up color wheel buttong
    gui.plotColorWheel = tk.PhotoImage(file='images/color_wheel.png')
    pcb_kwargs = {'image': gui.plotColorWheel, 'state': 'disabled',
                  'command': lambda: cf.pickPlotColor(gui), }
    gui.plotColorButton = tk.Button(parent, **pcb_kwargs)
    gui.plotColorButton.grid(row=2, column=3, sticky=tk.W, padx=(5, 0))


def buildAdditionalOptions(gui: tk.Tk, parent: tk.Frame,
                           waitFunc, startPlotFunc, ) -> None:
    """
    Adds elements for additional plot options:
        Grid lines (major/minor)
        Axis labels

    Parameters
    ----------
    gui : tk.Tk
        A tkinter GUI
    parent : tk.Frame
        A placeholder for all of these elements
    waitFunc : function
        A function pointer for having the GUI wait before acting
    startPlotFunc : function
        Kicks off the plot in the viewer pane

    Returns
    -------
    None

    """

    # - - - - - - - - - -
    # Row 0 - Grid
    gui.gridLabel = ttk.Label(parent, text='Gridlines:',)
    gui.gridLabel.grid(row=0, column=0, sticky=tk.W, padx=(0, 2))

    gui.gridMajor = tk.BooleanVar(value=True)
    gui.gridMinor = tk.BooleanVar(value=False)

    gmaj_kwargs = {'text': 'Major', 'variable': gui.gridMajor,
                   'command': lambda: startPlotFunc(1), }
    gmin_kwargs = {'text': 'Minor', 'variable': gui.gridMinor,
                   'command': lambda: startPlotFunc(1),
                   'state': 'disabled', }

    gui.gridMajorCB = tk.Checkbutton(parent, **gmaj_kwargs)
    gui.gridMajorCB.grid(row=0, column=1, sticky=tk.W,)

    gui.gridMinorCB = tk.Checkbutton(parent, **gmin_kwargs)
    gui.gridMinorCB.grid(row=0, column=2, sticky=tk.W,)

    # - - - - - - - - - -
    # Row 1 - Axis Labels
    gui.showAxLabel = ttk.Label(parent, text='Axis Labels:',)
    gui.showAxLabel.grid(row=1, column=0, sticky=tk.W, padx=(0, 2))
    gui.showAxFrame = tk.Frame(parent)
    gui.showAxFrame.grid(row=1, column=1, sticky=tk.W, columnspan=2)
    buildXYZGridLabels(gui, gui.showAxFrame, startPlotFunc)


def buildXYZGridLabels(gui: tk.Tk, parent: tk.Frame, startPlotFunc) -> None:
    """
    Builds the elements necessary for a user to decide whether grid labels
    are needed for X, Y, or Z

    Parameters
    ----------
    gui : tk.Tk
        A tkinter GUI
    parent : tk.Frame
        A placeholder for all of these elements
    startPlotFunc : TYPE
        Kicks off the plot in the viewer pane

    Returns
    -------
    None

    """

    # Row 0 - XYZ Labels
    gui.showXLabel = tk.BooleanVar(value=True)
    gui.showYLabel = tk.BooleanVar(value=True)
    gui.showZLabel = tk.BooleanVar(value=True)
    xlbl_kwargs = {'text': 'X', 'variable': gui.showXLabel,
                   'command': lambda: startPlotFunc(1), }
    ylbl_kwargs = {'text': 'Y', 'variable': gui.showYLabel,
                   'command': lambda: startPlotFunc(1), }
    zlbl_kwargs = {'text': 'Z', 'variable': gui.showZLabel,
                   'command': lambda: startPlotFunc(1), }

    gui.showXLabelCB = tk.Checkbutton(parent, **xlbl_kwargs)
    gui.showXLabelCB.grid(row=0, column=0, sticky=tk.W)
    gui.showYLabelCB = tk.Checkbutton(parent, **ylbl_kwargs)
    gui.showYLabelCB.grid(row=0, column=1, sticky=tk.W)
    gui.showZLabelCB = tk.Checkbutton(parent, **zlbl_kwargs)
    gui.showZLabelCB.grid(row=0, column=2, sticky=tk.W)


def buildRunSelector(gui: tk.Tk, parent: tk.Frame,
                     waitFunc, startPlotFunc, availableRuns) -> None:
    """
    Builds the elements necessary to downselect runs for viewing

    Parameters
    ----------
    gui : tk.Tk
        A tkinter GUI
    parent : tk.Frame
        A placeholder for all of these elements
    waitFunc : function
        A function pointer for having the GUI wait before acting
    startPlotFunc : function
        Kicks off the plot in the viewer pane
    availableRuns : list (str)
        The available runs for plotting to be displayed in the SpinBox

    Returns
    -------
    None
        DESCRIPTION.

    """

    # The switch for whether runs are plotted all together
    gui.showAllRuns = tk.BooleanVar(value=True)

    # - - - - - - - - - -
    # Row 0 - Show All Runs
    allruns_kwargs = {'text': 'All', 'var': gui.showAllRuns,
                      'value': True, 'command': lambda: startPlotFunc(1)}

    gui.allRunsRB = ttk.Radiobutton(parent, **allruns_kwargs,)
    gui.allRunsRB.grid(row=0, column=0, columnspan=1, sticky=tk.W)

    # - - - - - - - - - -
    # Row 1 - Show Some Runs
    someruns_kwargs = {'text': 'Select', 'var': gui.showAllRuns,
                       'value': False,
                       'command': lambda: startPlotFunc(1)}
    gui.someRunsRB = ttk.Radiobutton(parent, **someruns_kwargs,)
    gui.someRunsRB.grid(row=0, column=1, columnspan=1, sticky=tk.W)

    # Setting up the chooser for the individual run
    gui.run = tk.IntVar()
    run_kwargs = {'values': availableRuns.tolist(), 'width': 4,
                  'command': lambda: startPlotFunc(1), 'wrap': True,
                  'state': 'disabled', 'textvariable': gui.run, }
    gui.runChoice = ttk.Spinbox(parent, **run_kwargs)
    gui.runChoice.grid(row=0, column=2, sticky=tk.W)
    gui.runChoice.bind('<Key>', waitFunc)

    # If there is an available run, set it to the first one
    if availableRuns.size > 0:
        gui.runChoice.set(availableRuns[0])

    # Setting up transparency
    gui.transparentRuns = tk.BooleanVar(value=True)
    transRun_kwargs = {'text': 'Fade Others', 'state': 'disabled',
                       'variable': gui.transparentRuns,
                       'command': lambda: startPlotFunc(1), }

    gui.transRunsCB = tk.Checkbutton(parent, **transRun_kwargs)
    gui.transRunsCB.grid(row=0, column=3, sticky=tk.W,)


def buildEditorElements(gui: tk.Tk, parent: tk.Frame,
                        plotColumns, availableRuns,
                        waitFunc, startPlotFunc) -> None:
    """
    Builds the components to add to the editor frame and calls
    functions to build their subcomponents

    Parameters
    ----------
    gui : tk.Tk
        A tkinter GUI
    parent : tk.Frame
        A placeholder for all of these elements
    plotColumns : list (str)
        The available options for plotting to be displayed in the ComboBox
    availableRuns : list (str)
        The available runs for plotting to be displayed in the SpinBox
    waitFunc : function
        A function pointer for having the GUI wait before acting
    startPlotFunc : function
        Kicks off the plot in the viewer pane

    Returns
    -------
    None

    """
    # - - - - - - - - - - - - - - - -
    # Row 0 - XYZ Plot Columns
    thisrow = 0
    fieldsKwargs = {'relief': tk.RIDGE, 'text': "Fields to Plot", }
    fieldsFrame = ttk.LabelFrame(parent, **fieldsKwargs)
    fieldsFrame.grid(row=thisrow, column=1, sticky=tk.W, pady=(1, 0))

    xyz = buildXYZFieldSelectors(fieldsFrame, gui.plotCols, startPlotFunc)

    gui.xCol, gui.xCB = xyz[0]
    gui.yCol, gui.yCB = xyz[1]
    gui.zCol, gui.zCB = xyz[2]

    # - - - - - - - - - - - - - - - -
    # Row 1 - XYZ Min/Max Fields
    thisrow += 1
    xyzMinMaxFrame = ttk.LabelFrame(parent, text="Set Limits", relief=tk.RIDGE)
    xyzMinMaxFrame.grid(row=thisrow, column=1, sticky=tk.W, pady=3,)
    buildXYZMinMaxModifiers(gui, xyzMinMaxFrame, waitFunc)

    # - - - - - - - - - - - - - - - -
    # Row 2 - Custom Title
    thisrow += 1
    titleLF = ttk.LabelFrame(parent, text="Custom Title", relief=tk.RIDGE)
    titleLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3)
    buildCustomTitleOptions(gui, titleLF, waitFunc, startPlotFunc)

    # - - - - - - - - - - - - - - - -
    # Row 3 - Style Options
    thisrow += 1
    styleLF = ttk.LabelFrame(parent, text="Plot Style", relief=tk.RIDGE)
    styleLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3)
    buildStyleOptions(gui, styleLF, waitFunc, startPlotFunc)

    # - - - - - - - - - - - - - - - -
    # Row 4 - Additional Options
    thisrow += 1
    addOptsLF = ttk.LabelFrame(parent, relief=tk.RIDGE,
                               text="Additional Options",)
    addOptsLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3,)
    buildAdditionalOptions(gui, addOptsLF, waitFunc, startPlotFunc,)

    # - - - - - - - - - - - - - - - -
    # Row 5 - Run Traversal
    thisrow += 1
    runChoiceLF = ttk.LabelFrame(parent, relief=tk.RIDGE, text="Run Viewer",)
    runChoiceLF.grid(row=thisrow, column=1, sticky=tk.W, pady=3,)
    buildRunSelector(gui, runChoiceLF, waitFunc, startPlotFunc, availableRuns)


def buildEditAndViewPanes(parent,) -> tuple:
    """
    Creates the frames to hold the editing options and the viewer
    The width is set to 260 for the editPane and the viewPane will
    take up the rest of the available real estate.

    Parameters
    ----------
    parent : tkinter object
        Could be any type of tkinter object capable of holding frames

    Returns
    -------
    tuple
        Handles to the edit and view panes

    """

    # Defining Edit Pane
    editPane = ttk.Frame(parent, width=260, relief=tk.GROOVE)
    parent.add(editPane)

    # We don't want the edit frame to automatically resize
    editPane.grid_propagate(0)

    # Adds the plot viewer pane
    viewPane = ttk.Frame(parent,)
    parent.add(viewPane)

    return (editPane, viewPane)


def buildInputElements(gui: tk.Tk, parent, ) -> None:
    """
    Adds the elements needed to perform a data load.

    Parameters
    ----------
    gui : tk.Tk
        The top-level GUI instance
    parent : TYPE
        DESCRIPTION.

    Returns
    -------
    None

    """
    # - - - - - - - - - - - - - - - -
    # Row 0 - Browsing for Directory
    gui.topDirLabel = tk.Label(parent, text='Directory with Run(s): ')
    gui.topDirLabel.grid(row=0, sticky=tk.W)

    # TODO: Change this back to empty string
    gui.topDir = ef.absjoin(os.getcwd(), os.pardir, 'runs')
    gui.topDirPath = tk.Text(parent, relief=tk.SUNKEN)
    gui.topDirPath.insert(tk.INSERT, gui.topDir)
    gui.topDirPath.config(width=60, height=1.45)
    gui.topDirPath.grid(row=0, column=1, sticky=tk.W)

    gui.topDirBrowseButton = tk.Button(parent, text='Browse', height=1,
                                       command=lambda: cf.getTopDir(gui))
    gui.topDirBrowseButton.grid(row=0, column=6, padx=4)

    gui.topDirLoadButton = tk.Button(
                                parent,
                                text='Load',
                                height=1,
                                command=lambda: cf.loadFromTopDir(gui))
    gui.topDirLoadButton.grid(row=0, column=7, padx=4)

    # - - - - - - - - - - - - - - - -
    # Row 1 - Threat Type(s)
    gui.threatTypeOptions = ('Infer', 'ABT', 'TBM')
    gui.threatTypeLabel = tk.Label(parent, text='Threat: ')
    gui.threatTypeLabel.grid(row=1, sticky=tk.W)
    gui.threatType = tk.StringVar()
    gui.threatTypeCB = ttk.Combobox(parent, textvariable=gui.threatType,
                                    values=gui.threatTypeOptions, width=20,
                                    state='readonly',)

    gui.threatTypeCB.set('Infer')  # Could use .current(0)
    gui.threatTypeCB.grid(row=1, column=1, sticky=tk.W)
