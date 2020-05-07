# -*- coding: utf-8 -*-

# AICET Imports
import cef_sample_code as csc
import element_builder as eb

# System Imports
import numpy as np
import pandas as pd
import os
import sys

# Tkinter Imports
import tkinter as tk
from tkinter import ttk

# Dash Imports
import dash
import dash_core_components as dcc
import dash_html_components as html


def startDash():
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    dashApp = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    dashApp.layout = html.Div(children=[
        html.H1(children='Hello Dash'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='example-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2],
                     'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5],
                     'type': 'bar', 'name': u'Montréal'},
                ],
                'layout': {
                    'title': 'Dash Data Visualization'
                }
            }
        )
    ])
    dashApp.run_server(debug=True)
    return


class BrowserTest(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="images/window_icon_radar.ico")
        tk.Tk.wm_title(self, "ETESim Plotting Suite")
        self.geometry("850x550+150+50")

        self.missileDF = pd.read_csv(os.path.join(os.getcwd(), os.pardir,
                                                  'runs', 'out.csv'))
        self.plotCols = self.getPlotCols()

        # - - - - - - - - - - - - - - - -
        # Holder for editor/viewer
        graphPanes = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        graphPanes.pack(fill=tk.BOTH, expand=True)
        startURL = (f'http://localhost:8888/tree/'
                    f'OneDrive%20-%20Torch%20Technologies%2C%20Inc')
        dashURL = f'http://127.0.0.1:8050/'
        assert(startURL)
        assert(dashURL)
        startDash()
        editPane, viewPane = eb.buildEditAndViewPanes(graphPanes, browser=True,
                                                      url=dashURL)

        # Setting the starting run options
        fieldsKwargs = {'relief': tk.RIDGE, 'text': "Fields to Plot", }
        fieldsFrame = ttk.LabelFrame(editPane, **fieldsKwargs)
        fieldsFrame.grid(row=0, column=1, sticky=tk.W, pady=(1, 0))

        xyz = eb.buildXYZFieldSelectors(fieldsFrame, self.plotCols, self.plot)
        self.xCol, self.xCB = xyz[0]
        self.yCol, self.yCB = xyz[1]
        self.zCol, self.zCB = xyz[2]

    def on_root_configure(self, _):
        if self.browser_frame:
            self.browser_frame.on_root_configure()

    def on_configure(self, event):
        if self.browser_frame:
            width = event.width
            height = event.height
            if self.navigation_bar:
                height = height - self.navigation_bar.winfo_height()
            self.browser_frame.on_mainframe_configure(width, height)

    def on_focus_in(self, _):
        pass

    def on_focus_out(self, _):
        pass

    def on_close(self):
        if self.browser_frame:
            self.browser_frame.on_root_close()
        self.master.destroy()

    def get_browser(self):
        if self.browser_frame:
            return self.browser_frame.browser
        return None

    def get_browser_frame(self):
        if self.browser_frame:
            return self.browser_frame
        return None

    def plot(self, *args):
        pass

    def getPlotCols(self):
        cols = sorted([col for col, val in self.missileDF.dtypes.items()
                       if val == np.dtype('float64')])

        return [''] + cols


if __name__ == "__main__":
    errText = "CEF Python v55.3+ required to run this"
    assert csc.cef.__version__ >= "55.3", errText
    sys.excepthook = csc.cef.ExceptHook  # Shuts down CEF processes on error
    app = BrowserTest()
    # Tk must be initialized before CEF otherwise fatal error (Issue #306)
    csc.cef.Initialize()
    app.mainloop()
    csc.cef.Shutdown()