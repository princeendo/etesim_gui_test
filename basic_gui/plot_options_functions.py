# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 09:54:00 2020

@author: white
"""


def getLimits(gui, ax) -> tuple:
    """
    Returns the limits to be used in a plot based upon the default
    limits given by pyplot and the limits (potentially) specified
    by the user in the GUI

    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        A handle to the subplot which will have new limits
        This cannot be type hinted because the type is created
        on the fly

    Returns
    -------
    tuple
        A six-element tuple of the minimum and maximum values for
        x, y, and z, respectively

    """
    xMin, xMax = ax.get_xlim()
    if gui.xLimits.get():
        if gui.xMin.get() not in ['', 'Min']:
            xMin = float(gui.xMin.get())
        if gui.xMax.get() not in ['', 'Max']:
            xMax = float(gui.xMax.get())

    yMin, yMax = ax.get_ylim()
    if gui.yLimits.get():
        if gui.yMin.get() not in ['', 'Min']:
            yMin = float(gui.yMin.get())
        if gui.yMax.get() not in ['', 'Max']:
            yMax = float(gui.yMax.get())

    if gui.dimensions == 3:
        zMin, zMax = ax.get_zlim()
        if gui.zLimits.get():
            if gui.zMin.get() not in ['', 'Min']:
                zMin = float(gui.zMin.get())
            if gui.zMax.get() not in ['', 'Max']:
                zMax = float(gui.zMax.get())
    else:
        # This guarantees a six-element return tuple each time
        zMin, zMax = (0, 0)

    xyzLimits = (xMin, xMax, yMin, yMax, zMin, zMax)
    return xyzLimits