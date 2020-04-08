# -*- coding: utf-8 -*-
import tkinter as tk
import itertools as it


# Reference: https://www.tutorialspoint.com/python/tk_canvas.htm
class CanvasTest():
    def __init__(self, tk_root):
        self.root = tk_root

        # Creating a simple canvas to draw upon
        self.canvas = tk.Canvas(self.root, width=650, height=550)
        self.canvas.pack()

        # Creating a line segment
        # x and y values are pixel values from left and top, respectively
        self.line = self.canvas.create_line(100, 250,    # Start x/y
                                            360, 25,)    # End x/y
        self.canvas.itemconfigure(self.line, fill='red', width=10)

        # Equivalent to
        # self.multiline = self.canvas.create_line(25, 50,
        #                                          150, 150,
        #                                          250, 140,
        #                                          20, 50,
        #                                          fill='yellow', width=5)
        vertices = [(25, 50), (150, 150), (250, 140), (20, 50), ]
        vert_list = list(it.chain(vertices))
        self.multiline = self.canvas.create_line(*vert_list,
                                                 fill='yellow',
                                                 width=5)

        self.sampleText = self.canvas.create_text(80, 100,
                                                  text='Hello',
                                                  font=('Times', 15, 'bold'))

        # Rectangles are created by specifying two vertices
        upper_left = (175, 150)
        lower_right = (250, 175)
        self.rectangle = self.canvas.create_rectangle(*upper_left,
                                                      *lower_right,
                                                      fill='green',
                                                      width=2)

        # Ovals are created much like a rectangle.
        # But that doesn't make sense for an ellipse
        # Equivalent to
        # self.oval = self.canvas.create_oval(350, 350,
        #                                     250, 200)
        tall_or_fat = 'tall'
        semimajor_length = 150
        semiminor_length = 100
        center = (300, 275)
        xdiff = semiminor_length / 2.0
        ydiff = semimajor_length / 2.0
        if tall_or_fat == 'fat':    # Swap out if it's fat
            xdiff, ydiff = (ydiff, xdiff)
        upper_left = (center[0] - xdiff, center[1] - ydiff)
        lower_right = (center[0] + xdiff, center[1] + ydiff)
        self.oval = self.canvas.create_oval(*upper_left, *lower_right)

        # Creating an arc
        # I don't really care like figuring this out now
        self.arc = self.canvas.create_arc(120, 20,
                                          30, 80,
                                          fill='red',
                                          width=3,
                                          start=0,
                                          extent=180)

        # Adding an image onto the canvas
        self.icon = tk.PhotoImage(file='simple-icon.png')
        xy_loc = (175, 150)
        self.image = self.canvas.create_image(*xy_loc,
                                              image=self.icon,)
        # Brings the rectangle to the front
        self.canvas.lift(self.rectangle)


rt = tk.Tk()
rt.title('Canvas Sample')
rt.geometry('500x450')
app = CanvasTest(rt)
rt.mainloop()
