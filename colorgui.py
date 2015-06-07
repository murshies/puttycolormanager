
from collections import namedtuple
import tkinter as tk

import colorinterface

ColorGroup = namedtuple('ColorGroup', 'red green blue')

class ConfigDisplayWidgetOld(tk.Frame):
    def __init__(self, master, session_names):
        tk.Frame.__init__(self, master)
        self.master = master
        self.session_names = session_names
        
        self.session_list = tk.Listbox(
            self, selectmode=tk.EXTENDED)
        
        for name in self.session_names:
            session_display_name = name.replace('%20', ' ')
            self.session_list.insert(tk.END, session_display_name)

        self.session_list.grid(row=0, column=0)

class ConfigDisplayWidget(tk.Frame):
    def __init__(self, master, session_names):
        tk.Frame.__init__(self, master)
        self.master = master
        self.session_names = session_names
        
        self.session_list = tk.Listbox(
            self, selectmode=tk.EXTENDED)
        
        for name in self.session_names:
            session_display_name = name.replace('%20', ' ')
            self.session_list.insert(tk.END, session_display_name)

        self.session_list.pack(fill=tk.BOTH, expand=True)

class ColorValuesFrame(tk.Frame):
    def __init__(self, master, label_text):
        tk.Frame.__init__(self, master)
        
        label = tk.Label(self, text=label_text)
        label.pack(side=tk.LEFT, fill=tk.X)
        
        red_input = tk.Entry(self, width=5)
        red_input.pack(side=tk.RIGHT, fill=tk.Y)
        
        green_input = tk.Entry(self, width=5)
        green_input.pack(side=tk.RIGHT, fill=tk.Y)
        
        blue_input = tk.Entry(self, width=5)
        blue_input.pack(side=tk.RIGHT, fill=tk.Y)

class ColorValuesWidget(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.colorInputs = {}
        
        # Create the column for the inputs.
        for num, color in enumerate(colorinterface.PUTTY_COLOR_ORDER):
            next_input_group = ColorValuesFrame(self, color)
            next_input_group.pack(fill=tk.X)
            self.colorInputs[color] = next_input_group

class ColorValuesWidgetOld(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.colorInputs = {}

        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=0, column=0)

        for num, color in enumerate(colorinterface.PUTTY_COLOR_ORDER):
            nextLabel = tk.Label(self.canvas, text=color)
            nextLabel.grid(row=num, column=0, rowspan=1)
            redInput = tk.Entry(self.canvas, width=5)
            blueInput = tk.Entry(self.canvas, width=5)
            greenInput = tk.Entry(self.canvas, width=5)
            redInput.grid(row=num, column=1, rowspan=1)
            blueInput.grid(row=num, column=2, rowspan=1)
            greenInput.grid(row=num, column=3, rowspan=1)
            self.colorInputs[nextLabel] = ColorGroup(
                redInput, greenInput, blueInput)

class ColorInterfaceOld(tk.Frame):
    def __init__(self, master, session_names):
        tk.Frame.__init__(self, master)
        self.master = master
        
        # Initialize the sub-widgets.
        self.config_display = ConfigDisplayWidget(self, session_names)
        self.color_values = ColorValuesWidget(self)
        
        # Place the sub-widgets within the main frame.
        self.config_display.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.color_values.grid(row=0, column=1)
        
        # Place the main widget in the top level widget.
        self.grid(row=0)

class ColorInterface(tk.Frame):
    def __init__(self, master, session_names):
        tk.Frame.__init__(self, master)
        self.master = master
        
        # Initialize the sub-widgets.
        self.config_display = ConfigDisplayWidget(self, session_names)
        self.color_values = ColorValuesWidget(self)
        
        # Place the sub-widgets within the main frame.
        self.config_display.pack(side=tk.LEFT, fill=tk.BOTH)
        self.color_values.pack(side=tk.RIGHT)

def main():
    '''Initialize the window and enter the Tkinter main loop.'''
    top = tk.Tk()
    interface = ColorInterface(top, colorinterface.getAllSessionNames())
    interface.pack()
    tk.mainloop()

if __name__ == '__main__':
    main()

