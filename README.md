# etesim_gui_test
Documentation of Progress on ETESim GUI

## 1. Learning Progress
### 1.1 Python Tkinter Masterclass (Udemy)
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