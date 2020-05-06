import cef_sample_code as csc
import element_builder as eb
import tkinter as tk
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
        self.xCB['values'] = self.plotCols
        self.yCB['values'] = self.plotCols
        self.zCB['values'] = self.plotCols

        # - - - - - - - - - - - - - - - -
        # Holder for editor/viewer
        self.graphPanes = ttk.Panedwindow(self.viewTab, orient=tk.HORIZONTAL)
        self.graphPanes.pack(fill=tk.BOTH, expand=True)

        eb.addEditorAndViewPanes(self, self.graphPanes, self.plotCols,
                                 self.availableRuns, self.waitToPlot,
                                 self.startPlot)

        # Setting the starting run options
        # cf.setRunOptions(self, )
        
        eb.buildXYZFieldSelector(self, self.editPane, )

if __name__ == "__main__":
    errText = "CEF Python v55.3+ required to run this"
    assert csc.cef.__version__ >= "55.3", errText
    sys.excepthook = csc.cef.ExceptHook  # Shuts down CEF processes on error
    app = BrowserTest()
    # Tk must be initialized before CEF otherwise fatal error (Issue #306)
    csc.cef.Initialize()
    app.mainloop()
    csc.cef.Shutdown()
