# etesim_gui_test
Documentation of Progress on ETESim GUI

## 1. Learning Progress
### 1.1 [Python Tkinter Masterclass](https://www.udemy.com/course/python-tkinter-masterclass/)
I enrolled in this class to try to learn the "correct" way to do Python GUI programming. There are multiple modules that I will be going through
#### 1.1.1 Basic Widgets
This should get me up to speed on the basics of tkinter development
##### 1.1.1.1 Creating Your First GUI Application
I successfully completed this using tkinter and ttk. Nothing really to show.
##### 1.1.1.2 Using Labels
I was able to complete this project and add a label to my GUI.
##### 1.1.1.3 Using Buttons
I successfully added a button with a label to the GUI. Clicking does nothing.
##### 1.1.1.4 Using an Entry Widget
I successfully built a GUI which has three separate fields to enter data. One was made with ttk and the others with tkinter. A password field with asterisks was part of this program, though I see little need for this in my goals. I updated the code from the tutorial to be done with classes instead of using global variables.
##### 1.1.1.5 Grid Layout
I successfully built a GUI with a grid layout while specifying columns, rows, widths, and locations. I, again, used a class methodology instead of the somewhat terrible version using globals for callback functions. I learned about spanning items across columns and how to capture input and print the values to the command line for verification
##### 1.1.1.6 Using CheckBoxes
I updated the previous GUI to include several fields for text entry and a checkbox which contains a boolean value to verify behavior. The codebase has been translated to an object-oriented design instead for all objects except root. This will be updated at some point.
##### 1.1.1.7 Radio Buttons
The GUI has been updated to include radio buttons to switch between values. This will need to somehow be turned into frames in case multiple radio sets need to be considered. This may not be necessary if we use separate variables for storing the value. Needs more investigation
##### 1.1.1.8 ComboBox
The GUI has been updated to include a dropdown menu for several options. This is exactly the step I needed for picking the parameters to graph. Updating the options list will be tricky.
##### 1.1.1.9 SpinBox
The GUI has been updated to include a "spinbox" which has a range of values (instead of a category list) that you can "spin" through.
##### 1.1.1.10 MessageBox
A separate GUI has been developed which puts up pop-up windows to either inform you or query a yes/no response. I'm not sure of the best use for this right now.
##### 1.1.1.11 Text Editor
A separate GUI has been developed which has a box for entering text that can be captured into a variable. I'm not sure of the best use for this right now.
##### 1.1.1.12 Place Geometry Manager
A separate GUI has been developed which describes how to place objects by manually specifying absolute or relative coordinates. Auto-scales relative coordinates. May prove useful.
##### 1.1.1.13 Frames
A separate GUI has been developed which describes how to develop frames (which seem like sub-GUIs) and how to place them.
#### 1.1.2 Advanced Widgets
These additional features will be useful for building a robust GUI
##### 1.1.2.14 ProgressBar
A separate GUI has been developed which can be used to show the progress of a program.
##### 1.1.2.15 PanedWindow widget
A separate GUI has been developed which segments a GUI into panes for different displays.
##### 1.1.2.16 Tabs
A standalone GUI has been developed which shows different tabs for segmenting a display.
##### 1.1.2.17 ListBox Widget
A standalone GUI has been deveoped which shows items in a list which can be selected.
##### 1.1.2.18 Using Images
A standalone GUI has been developed for displaying images.
##### 1.1.2.19 How to Create a Menu for Our Apps
A standalone GUI has been developed which has drop-down menus (which don't do anything but allow you to quit).
##### 1.1.2.20 How to Create the TreeView Widget
A standalone GUI with a list display in tree format (so it collapses) has been developed.
##### 1.1.2.21 Creating a Scrollbar
A standalone GUI which has a scrollbar for a text box has been developed.
##### 1.1.2.22 Using the Canvas Widget
A standalone GUI demonstrating how to place geometric objects has been developed.
##### 1.1.2.23 Using Style for Our Apps
This section was skipped because it is likely not relevant.
##### 1.1.2.24 Using Open file Dialog
A standalone GUI which opens a text file and displays its contents in a text box has been developed.
##### 1.1.2.25 Save File Dialog
The previous GUI has been extended to allow for the contents of a text box to be saved into a file.
##### 1.1.2.26 Color Dialog
The previous GUI has been extended to change the color of the text inside.
## X. TODO List
### X.1 Backend
* Dictionary for mapping internal variables to human-readable names
* Method for downselection of data
* Criteria for downselection of data
### X.2 GUI Needs
* Directory selector for top-level
* Directory selector for output
* Slider for choosing between multiple runs (Spinbox instead?)
* Save button for graph
### X.3 User Options
* Display or save
* Downsample graphs
* Color picking of graphs
* Line style for graphs (_e.g._, dashed)
* Scatter instead of plot
### X.2 Repository wishlist
* Have every script name match the README.md header name