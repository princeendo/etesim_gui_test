import cef_sample_code as csc
import element_builder as eb
import tkinter as tk
import numpy as np
import pandas as pd
import os
import sys

from tkinter import ttk


class BrowserTest(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        tk.Tk.iconbitmap(self, default="images/window_icon_radar.ico")
        tk.Tk.wm_title(self, "ETESim Plotting Suite")
        self.geometry("850x550+150+50")

        self.df = pd.read_csv(os.path.join(os.getcwd(), os.pardir,
                                           'runs', 'out.csv'))
        self.plotCols = [''] + sorted([col for col, val
                                       in self.df.dtypes.items()
                                       if val == np.dtype('float64')])

        # - - - - - - - - - - - - - - - -
        # Holder for editor/viewer
        graphPanes = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        graphPanes.pack(fill=tk.BOTH, expand=True)
        self.editPane, self.viewPane = eb.buildEditAndViewPanes(graphPanes,
                                                                use_weird=True)

        # Setting the starting run options
        fieldsKwargs = {'relief': tk.RIDGE, 'text': "Fields to Plot", }
        fieldsFrame = ttk.LabelFrame(self.editPane, **fieldsKwargs)
        fieldsFrame.grid(row=0, column=1, sticky=tk.W, pady=(1, 0))

        xyz = eb.buildXYZFieldSelectors(fieldsFrame, self.plotCols, self.plot)
        self.xCol, self.xCB = xyz[0]
        self.yCol, self.yCB = xyz[1]
        self.zCol, self.zCB = xyz[2]

        # NavigationBar
#        self.navigation_bar = csc.NavigationBar(self.viewPane)
#        self.navigation_bar.grid(row=0, column=0,
#                                 sticky=(tk.N + tk.S + tk.E + tk.W))
#        
#        self.browser_frame = csc.BrowserFrame(self.viewPane, self.navigation_bar)
#        self.browser_frame.grid(row=1, column=0,
#                                sticky=(tk.N + tk.S + tk.E + tk.W))

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


if __name__ == "__main__":
    errText = "CEF Python v55.3+ required to run this"
    assert csc.cef.__version__ >= "55.3", errText
    sys.excepthook = csc.cef.ExceptHook  # Shuts down CEF processes on error
    app = BrowserTest()
    # Tk must be initialized before CEF otherwise fatal error (Issue #306)
    csc.cef.Initialize()
    app.mainloop()
    csc.cef.Shutdown()
