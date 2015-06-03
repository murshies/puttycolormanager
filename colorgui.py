
import tkinter as tk

import colorinterface

class ColorInterface(tk.Frame):
    def __init__(self, master, session_names):
        tk.Frame.__init__(self, master)
        self.session_names = session_names
        
        # Initialize the session Listbox.
        scrollbar = tk.Scrollbar(master, orient=tk.VERTICAL)
        self.session_list = tk.Listbox(
            master, selectmode=tk.EXTENDED, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.session_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.session_list.pack(side=tk.LEFT, fill=tk.Y, expand=1)
        
        for name in session_names:
            session_display_name = name.replace('%20', ' ')
            self.session_list.insert(tk.END, session_display_name)
        
def main():
    '''Initialize the window and enter the Tkinter main loop.'''
    top = tk.Tk()
    interface = ColorInterface(top, colorinterface.getAllSessionNames())
    
    tk.mainloop()

if __name__ == '__main__':
    main()

