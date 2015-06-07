
from collections import namedtuple
import tkinter as tk

import colorinterface

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

class ColorInterface(tk.Frame):
    def __init__(self, master, session_names):
        tk.Frame.__init__(self, master)
        self.master = master
        
        # Initialize the sub-widgets.
        display_frame = tk.Frame(self)
        config_display = ConfigDisplayWidget(display_frame, session_names)
        color_values = ColorValuesWidget(display_frame)
        
        # Place the sub-widgets within the display frame.
        config_display.pack(side=tk.LEFT, fill=tk.BOTH)
        color_values.pack(side=tk.RIGHT)
        
        # Initialize the button frame.
        button_frame = ButtonFrame(self)
        
        # Add the display and button frames to the main frame.
        display_frame.pack()
        button_frame.pack()

    def load_selected(self):
        print('load selected')
        
    def load_from_file(self):
        print('load from file')
        
    def apply_to_selected(self):
        print('apply to selected')
        
    def save_to_file(self):
        print('save to file')

class ButtonFrame(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        
        # Initialize the buttons.
        load_selected = tk.Button(
            self, text='Load Selected',
            command=lambda: self._load_selected_callback())
        load_selected.pack(side=tk.LEFT)
        
        load_from_file = tk.Button(
            self, text='Load From File',
            command=lambda: self._load_from_file_callback())
        load_from_file.pack(side=tk.LEFT)
        
        apply_to_selected = tk.Button(
            self, text='Apply To Selected',
            command=lambda: self._apply_to_selected_callback())
        apply_to_selected.pack(side=tk.LEFT)
        
        save_to_file = tk.Button(
            self, text='Save To File',
            command=lambda: self._save_to_file_callback())
        save_to_file.pack(side=tk.LEFT)
        
    def _load_selected_callback(self):
        self.master.load_selected()
        
    def _load_from_file_callback(self):
        self.master.load_from_file()
        
    def _apply_to_selected_callback(self):
        self.master.apply_to_selected()
        
    def _save_to_file_callback(self):
        self.master.save_to_file()

def main():
    '''Initialize the window and enter the Tkinter main loop.'''
    top = tk.Tk()
    interface = ColorInterface(top, colorinterface.getAllSessionNames())
    interface.pack()
    tk.mainloop()

if __name__ == '__main__':
    main()

