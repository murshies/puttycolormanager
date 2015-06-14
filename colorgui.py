
from collections import namedtuple
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

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
        
    def get_selected(self):
        return [self.session_list.get(x).replace(' ', '%20')
                for x in self.session_list.curselection()]

class ColorValuesFrame(tk.Frame):
    def __init__(self, master, label_text):
        tk.Frame.__init__(self, master)
        
        label = tk.Label(self, text=label_text)
        label.pack(side=tk.LEFT, fill=tk.X)
        
        self.red_input = tk.Entry(self, width=5)
        self.red_input.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.green_input = tk.Entry(self, width=5)
        self.green_input.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.blue_input = tk.Entry(self, width=5)
        self.blue_input.pack(side=tk.RIGHT, fill=tk.Y)

    def set_colors(self, colors):
        # Clear the inputs of any text.
        self.red_input.delete(0, tk.END)
        self.green_input.delete(0, tk.END)
        self.blue_input.delete(0, tk.END)
        
        # Set the new text.
        self.red_input.insert(0, colors[0])
        self.green_input.insert(0, colors[1])
        self.blue_input.insert(0, colors[2])
        
    def _convert_color(self, color_str):
        color = int(color_str)
        if color < 0 or color > 255:
            raise ValueError('Color component must be 0-255, inclusive.')
        return color

    def get_colors(self):
        return (self._convert_color(self.red_input.get()),
                self._convert_color(self.green_input.get()),
                self._convert_color(self.blue_input.get()))

class ColorValuesWidget(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        self.color_inputs = {}
        
        # Create the column for the inputs.
        for num, color in enumerate(colorinterface.PUTTY_COLOR_ORDER):
            next_input_group = ColorValuesFrame(self, color)
            next_input_group.pack(fill=tk.X)
            self.color_inputs[color] = next_input_group
            
    def load_colors(self, colors_list):
        for pos, color_tuple in enumerate(colors_list):
            color_name = colorinterface.PUTTY_COLOR_ORDER[pos]
            self.color_inputs[color_name].set_colors(color_tuple)
    
    def get_current_entry(self):
        '''Create a colors list in the same format as
        colorinterface.read_session_colors from the currently inputted
        values.'''
        colors_list = []
        for color_name in colorinterface.PUTTY_COLOR_ORDER:
            colors_list.append(self.color_inputs[color_name].get_colors())
        return colors_list

class ColorInterface(tk.Frame):
    def __init__(self, master, session_names):
        tk.Frame.__init__(self, master)
        self.master = master
        
        # Initialize the sub-widgets.
        display_frame = tk.Frame(self)
        self.config_display = ConfigDisplayWidget(display_frame, session_names)
        self.color_values = ColorValuesWidget(display_frame)
        
        # Place the sub-widgets within the display frame.
        self.config_display.pack(side=tk.LEFT, fill=tk.BOTH)
        self.color_values.pack(side=tk.RIGHT)
        
        # Initialize the button frame.
        button_frame = ButtonFrame(self)
        
        # Add the display and button frames to the main frame.
        display_frame.pack()
        button_frame.pack()
        
    def _invalid_inputs_message(self, dialog_title):
        error_lines = [
            'There are one or more invalid values in the input boxes.',
            'Please make sure that all inputs are integers in the range',
            '0 to 255, inclusive.'
        ]
        messagebox.showerror(
            title=dialog_title,
            message='\n'.join(error_lines))

    def load_selected(self):
        curr_selections = self.config_display.get_selected()
        if curr_selections:
            used_session = curr_selections[0]
            session_colors = colorinterface.read_session_colors(used_session)
            self.color_values.load_colors(session_colors)
        
    def load_from_file(self):
        dialog_title = 'Load From File'
        filename = filedialog.askopenfilename()
        if filename:
            try:
                colors_list = colorinterface.read_colors_from_INI(filename)
                self.color_values.load_colors(colors_list)
            except KeyError:
                messagebox.showerror(
                    title=dialog_title,
                    message=('Malformed INI file. Please ensure that the file '
                             'contains the color definitions in a section '
                             'called "{0}"').format(
                                 colorinterface.COLOR_INI_SECTION_NAME))
            except Exception as e:
                messagebox.showerror(
                    title=dialog_title,
                    message='Could not load colors from {0}:\n\n{1}'.format(
                        filename, e))
        
    def apply_to_selected(self):
        dialog_title = 'Apply to Selected'
        try:
            colors_from_inputs = self.color_values.get_current_entry()
            curr_selections = self.config_display.get_selected()
            if not curr_selections:
                messagebox.showerror(
                    title=dialog_title,
                    message='Please select one or more PuTTY sessions.')
            else:
                for selection in curr_selections:
                    colorinterface.write_session_colors(
                        selection, colors_from_inputs)
                messagebox.showinfo(
                    title=dialog_title,
                    message=('Applied the current color selection to the '
                             'selected PuTTY sessions successfully.'))
        except ValueError:
            self._invalid_inputs_message(dialog_title)
        
    def save_to_file(self):
        dialog_title = 'Save to File'
        try:
            colors_from_inputs = self.color_values.get_current_entry()
            filename = filedialog.asksaveasfilename()
            if filename:
                colorinterface.write_colors_to_INI(filename, colors_from_inputs,
                                                   color_names=True)
                messagebox.showinfo(
                    title=dialog_title,
                    message='Wrote colors to {0} successfully.'.format(filename))
        except ValueError as e:
            self._invalid_inputs_message(dialog_title)
        except Exception as e:
            messagebox.showerror(
                title=dialog_title,
                message='Could not save the colors to file:\n\n{0}'.format(e))

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
    interface = ColorInterface(top, colorinterface.get_all_session_names())
    interface.pack()
    tk.mainloop()

if __name__ == '__main__':
    main()

