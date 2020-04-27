# -*- coding: utf-8 -*-

# Module-Level Imports
import os
import re
import platform
import numpy as np
import pandas as pd

# Tkinter imports
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter import filedialog
import tkinter.font as font
import tkinter.colorchooser as tkColorChooser

# matplotlib imports
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# The original function was deprecated so we're importing the new one
# to match tutorials more closely
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

# Imports and settings for Tkinter
import matplotlib
matplotlib.use("TkAgg")  # To use with Tkinter

# Trying stuff out with plotly
import plotly.graph_objs as go
import random

import mplcursors


class mplSandbox(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="images/window_icon_radar.ico")
        tk.Tk.wm_title(self, "Matplotlib Sandbox")
        self.geometry("960x540+350+250")

        self.dimensions = 2

        self.whole = tk.Frame(self,)
        self.whole.pack(fill=tk.BOTH, expand=True)

        self.figure = plt.Figure()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.whole)
        self.canvas.draw()
        
        x = np.linspace(-np.pi, np.pi, 100)
        y = np.sin(x)

        self.mplPlot()
        # self.stdPlot(x, y)     
        # self.plotlyPlot()
        
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM,
                                         fill=tk.BOTH,
                                         expand=True)
        
    def mplPlot(self, ):
        myplot = self.figure.add_subplot(111, )
        harmonics = np.linspace(1, 3, 5)
        x = np.linspace(-np.pi, np.pi, 100)
        for h in harmonics:
            myplot.plot(x, np.sin(h * x))
            myplot.grid(which='both')
        mplcursors.cursor(myplot)
            
        

    def stdPlot(self, x, y):
        # Setting up subplot for showing all the plots
        subplot_kwargs = {'projection': '3d' if self.dimensions == 3 else None}
        myplot = self.figure.add_subplot(111, **subplot_kwargs)
        myplot.plot(x, y)
        myplot.grid(which='both')
        
    def plotlyPlot(self, ):
        f = go.FigureWidget()
        f.layout.hovermode = 'closest'
        f.layout.hoverdistance = -1 # ensures no "gaps" for selecting sparse data
        default_linewidth = 2
        highlighted_linewidth_delta = 2
        
        # just some traces with random data points  
        num_of_traces = 5
        random.seed = 42
        for i in range(num_of_traces):
            y = [random.random() + i / 2 for _ in range(100)]
            trace = go.Scatter(y=y, mode='lines', line={ 'width': default_linewidth })
            f.add_trace(trace)
        
        # our custom event handler
        def update_trace(trace, points, selector):
            # this list stores the points which were clicked on
            # in all but one event they it be empty
            if len(points.point_inds) > 0:
                for i in range( len(f.data) ):
                    f.data[i]['line']['width'] = default_linewidth + highlighted_linewidth_delta * (i == points.trace_index)
        
        
        # we need to add the on_click event to each trace separately       
        for i in range( len(f.data) ):
            f.data[i].on_click(update_trace)
        
        # let's show the figure 
        f.show()



if __name__ == "__main__":
    app = mplSandbox()
    try:
        assert Axes3D  # to silence the linter
        app.mainloop()
    except KeyboardInterrupt:
        app.destroy()
        print('Terminated')