
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

import colorinterface

"""
colorgui.py

This file contains the classes that create the main UI and allow user
interaction. It consists of three main components: the configuration
display (ConfigDisplayWidget), the color values display
(ColorValuesWidget), and the buttons (ButtonFrame). There are currently
four supported actions for interaction with PuTTY sessions: loading one
of the currently-selected PuTTY sessions as the colors in the entry
fields, loading the colors from a file, applying the colors from the
entry fields to the currently-selected PuTTY sessions, and saving the
entered color values to a file.
"""

class ConfigDisplayWidget(tk.Frame):
    """
    a Tkinter widget for displaying the list of PuTTY configurations
    
    It contains a Tkinter Listbox, whose values are the names of the
    PuTTY sessions found in the Windows registry. Spaces, which are
    expressed as %20 in the registry, are converted to actually spaces
    for the display. The selection of multiple PuTTY sessions is
    allowed.
    """
    
    def __init__(self, master, session_names):
        """
        Parameters
        ----------
        master : tkinter.Frame
            the parent widget; this will be an instance of a
            ColorInterface
        session_names : list
            the PuTTY session names from the Windows registry as a list
            of strings
        """
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
        """
        Get the currently selected PuTTY sessions. The names from the
        Listbox are converted back into their registry format (i.e.
        spaces are converted back into %20).
        
        Returns
        -------
        list
            a list of strings, each element corresponding to the
            registry-style name of a selected PuTTY session
        """
        return [self.session_list.get(x).replace(' ', '%20')
                for x in self.session_list.curselection()]

class ColorValuesFrame(tk.Frame):
    """
    a Tkinter widget for displaying a set of inputs for a single RGB
    integer tuple
    
    It consists of a label with the name of the color and three entry
    fields for red, green, and blue color values, in that order. The
    label is the name given to the color within the PuTTY dialog (i.e.
    the names in colorinterface.PUTTY_COLOR_ORDER).
    """
    
    def __init__(self, master, label_text):
        """
        Parameters
        ----------
        master : tkinter.Frame
            the parent widget; this will be an instance of a
            ColorValuesWidget
        label_text : string
            the text to display as the color name
        """
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
        """
        Display a new set of values for this color.
        
        Parameters
        ----------
        colors : tuple
            a tuple of RGB values, where each value is a string
        """
        # Clear the inputs of any text.
        self.red_input.delete(0, tk.END)
        self.green_input.delete(0, tk.END)
        self.blue_input.delete(0, tk.END)
        
        # Set the new text.
        self.red_input.insert(0, colors[0])
        self.green_input.insert(0, colors[1])
        self.blue_input.insert(0, colors[2])
        
    def _convert_color(self, color_str):
        """
        a helper method that converts the value from one of the inputs
        into an integer.
        
        See Also
        --------
        ColorValuesFrame.get_colors
        """
        color = int(color_str)
        if color < 0 or color > 255:
            raise ValueError('Color component must be 0-255, inclusive.')
        return color

    def get_colors(self):
        """
        Retrieve the current RGB values from this object's inputs.
        
        Returns
        -------
        tuple
            the RGB components in the form of integers
        
        Raises
        ------
        ValueError
            when one or more input value isn't a value RGB component
        """
        return (self._convert_color(self.red_input.get()),
                self._convert_color(self.green_input.get()),
                self._convert_color(self.blue_input.get()))

class ColorValuesWidget(tk.Frame):
    """
    a Tkinter widget for displaying all color inputs
    
    It is a series of ColorValuesFrame components stacked on top of each
    other.
    """
    
    def __init__(self, master):
        """
        Parameters
        ----------
        master : tkinter.Frame
            the parent widget; this will be an instance of a
            ColorInterface
        """
        tk.Frame.__init__(self, master)
        self.master = master
        self.color_inputs = {}
        
        # Create the column for the inputs.
        for num, color in enumerate(colorinterface.PUTTY_COLOR_ORDER):
            next_input_group = ColorValuesFrame(self, color)
            next_input_group.pack(fill=tk.X)
            self.color_inputs[color] = next_input_group
            
    def load_colors(self, colors_list):
        """
        Take a colors list and fill the corresponding ColorValuesFrames
        with their values.
        
        Parameters
        ----------
        color_list : list
            a list of RGB integer tuples
        
        See Also
        --------
        colorinterface.read_session_colors for more information on the
        color list format
        """
        for pos, color_tuple in enumerate(colors_list):
            color_name = colorinterface.PUTTY_COLOR_ORDER[pos]
            self.color_inputs[color_name].set_colors(color_tuple)
    
    def get_current_entry(self):
        """
        Create a colors list from the currently-entered values .
        
        Returns
        -------
        list
            a list of RGB integer tuples
        
        See Also
        --------
        colorinterface.read_session_colors for more information on the
        color list format
        """
        colors_list = []
        for color_name in colorinterface.PUTTY_COLOR_ORDER:
            colors_list.append(self.color_inputs[color_name].get_colors())
        return colors_list

class ColorInterface(tk.Frame):
    """
    This is the top-level frame for this application; it sits directly
    under the master Tk object.
    """
    
    def __init__(self, master, session_names):
        """
        Parameters
        ----------
        master : tkinter.Tk
            the master Tk object for this application
        session_names : list
            a list of PuTTY session names read from the Windows
            registry, each in the form of a string
        """
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
        """
        a helper method that displays an error dialog when one or more
        RGB component inputs (across all colors) are invalid
        
        Parameters
        ----------
        dialog_title : string
            the text to display as the window title for the error dialog
        """
        error_lines = [
            'There are one or more invalid values in the input boxes.',
            'Please make sure that all inputs are integers in the range',
            '0 to 255, inclusive.'
        ]
        messagebox.showerror(
            title=dialog_title,
            message='\n'.join(error_lines))

    def load_selected(self):
        """
        Read the colors of the first (as in highest in the Listbox)
        selected PuTTY session from the Windows registry and displays
        them in the entry fields. This is the logic that is run when the
        "Load Selected" button is pressed.
        """
        curr_selections = self.config_display.get_selected()
        if curr_selections:
            used_session = curr_selections[0]
            session_colors = colorinterface.read_session_colors(used_session)
            self.color_values.load_colors(session_colors)
        
    def load_from_file(self):
        """
        Ask the user for a INI file name using a file selection dialog,
        read the color values, and display them in the entry fields.
        Partial or invalid data is handled by displaying error messages.
        This is the logic that is run when the "Load From File" button
        is pressed.
        """
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
        """
        Take the colors from the entry fields and write the values to
        the Windows registry for all selected PuTTY sessions. Partial or
        invalid data and no PuTTY sessions being selected are handled by
        displaying error messages. This is the logic that is run when
        the "Apply To Selected" button is pressed.
        """
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
        """
        Take the colors from the entry fields and create a new INI file
        with their values. The user is presented a typical "save as"
        dialog for selecting the file name. This is the logic that is
        run when the "Save To File" button is pressed.
        """
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
    """
    a widget that contains all of the buttons present in the UI.
    
    This is displayed at the very bottom of the window and takes up the
    entire width.
    """
    
    def __init__(self, master):
        """
        Parameters
        ----------
        master : tkinter.Frame
            the parent widget; this will be an instance of a
            ColorInterface
        """
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
        """
        The callback for the "Load Selected" button.
        
        See Also
        --------
        ColorInterface.load_selected
        """
        self.master.load_selected()
        
    def _load_from_file_callback(self):
        """
        The callback for the "Load From File" button.
        
        See Also
        --------
        ColorInterface.load_from_file
        """
        self.master.load_from_file()
        
    def _apply_to_selected_callback(self):
        """
        The callback for the "Apply To Selected" button.
        
        See Also
        --------
        ColorInterface.apply_to_selected
        """
        self.master.apply_to_selected()
        
    def _save_to_file_callback(self):
        """
        The callback for the "Save To File" button.
        
        See Also
        --------
        ColorInterface.save_to_file
        """
        self.master.save_to_file()

def main():
    """Initialize the window and enter the Tkinter main loop."""
    top = tk.Tk()
    top.wm_title('PuTTY Color Manager')
    interface = ColorInterface(top, colorinterface.get_all_session_names())
    interface.pack()
    tk.mainloop()

if __name__ == '__main__':
    main()

