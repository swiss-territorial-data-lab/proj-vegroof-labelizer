import numpy as np
import tkinter as tk
from tkinter import Label, Frame, Text, messagebox, Checkbutton, Toplevel
from tkinter import ttk
from tkinter.ttk import Combobox
from ttkwidgets import CheckboxTreeview
from functools import partial
import threading


def thread_restart_buffer(self):
    """
    Restarts the buffer in a separate thread, manages potential errors, and updates UI information.

    Parameters:
        self: object - The instance of the class calling this function.

    Returns:
        None
    """
    # Reset buffer and then update shown infos
    try:
        self.buffer.restart(self.buffer_front_max_size, self.buffer_back_max_size, self.margin_around_image)
    except Exception as e:
        print("An error occured while restarting buffer: ", e)
        # try:
        #     save(self, verbose=False)
        #     print("For safety measures, the current state of the work was saved.")
        # except Exception as e:
        #     print("During the management of the error, the program tried to save the work but did not manage due to the following error", e)
        
    finally:
        self.loading_running = False
        self.update_infos()
        self.show_image()
        self.buffer_infos_lbl.config(text="")
        set_all_states(self.root, 'normal', self.menu_bar)


def set_all_states(parent, state, menu=None):
    """
    Recursively sets the state of all widgets in a parent container and optionally updates a menu's state.

    Parameters:
        parent: Widget - The parent container whose children states will be updated.
        state: str - The state to apply ('normal', 'disabled', etc.).
        menu: Menu (optional) - The menu whose entries' states will be updated.

    Returns:
        None
    """
    for child in parent.winfo_children():
        if isinstance(child, (ttk.Button, Text, ttk.Combobox)):
            child.config(state=state)
        elif isinstance(child, Frame):
            set_all_states(child, state)
    if menu:   
        for i in range(menu.index('end') + 1):  # Iterate through all items
            menu.entryconfig(i, state=state)


def menu_mode_choice(self, mode_window):
    """
    Handles the user interaction for selecting and configuring the mode of operation 
    in the application's interface.

    This function displays a configuration window allowing users to choose between 
    'labelizer' and 'correcter' modes. It validates user inputs for missing or duplicate 
    values, maps column values to labels, and updates relevant attributes based on 
    the chosen mode.

    Args:
        self: Reference to the parent class instance containing the application's state.
        mode_window (tk.Toplevel): The pop-up window for mode selection and configuration.

    Returns:
        return_value: used to make the main process wait for this menu to be completed before continuing the loading 
        upon successful configuration or displays warnings for invalid inputs.
    """

    def ok_button_pressed(return_value, event=None):
        if combobox_mode.get() == 'labelizer':
            # test if nothing missing
            if do_select_col.get() == 1.0:
                if combobox_select_col.get() == "Select":
                    messagebox.showwarning("warning", "Missing values!")
                    mode_window.focus_set()
                    return

                lst_values = list(self.new_dataset[combobox_select_col.get()].unique())
                for idx, textbox in enumerate(lst_vals_select_col_lbl):
                    if lst_vals_select_col_val[idx].cget('text') in lst_values and textbox.get("1.0", "end-1c") == "":
                        messagebox.showwarning("warning", "Missing values!")
                        mode_window.focus_set()
                        return
                    
                lst_labels = [textbox.get("1.0", "end-1c") for textbox in lst_vals_select_col_lbl if textbox.get("1.0", "end-1c") != ""]
                if len(lst_labels) > len(set(lst_labels)):
                        messagebox.showwarning("warning", "Duplicate values in select column's labels!")
                        mode_window.focus_set()
                        return

            if text_interest_col_create.get("1.0", "end-1c") == "":
                messagebox.showwarning("warning", "Missing values!")
                mode_window.focus_set()
                return

            no_interest_lbl = True
            for textbox in lst_vals_interest_col_lbl:
                if textbox.get("1.0", "end-1c") != "":
                    no_interest_lbl = False
                    break
            if no_interest_lbl:
                messagebox.showwarning("warning", "Missing values!")
                mode_window.focus_set()
                return

            for idx, textbox in enumerate(lst_vals_interest_col_lbl):
                if textbox.get("1.0", "end-1c") != "":
                    if lst_vals_interest_col_val[idx].get("1.0", "end-1c") == "":
                        messagebox.showwarning("warning", "Missing values!")
                        mode_window.focus_set()
                        return                    
            lst_labels = [textbox.get("1.0", "end-1c") for textbox in lst_vals_interest_col_lbl if textbox.get("1.0", "end-1c") != ""]
            if len(lst_labels) > len(set(lst_labels)):
                    messagebox.showwarning("warning", "Duplicate values in interest column's labels!")
                    mode_window.focus_set()
                    return                    
            lst_vals = [textbox.get("1.0", "end-1c") for textbox in lst_vals_interest_col_val if textbox.get("1.0", "end-1c") != ""]
            if len(lst_vals) > len(set(lst_vals)):
                    messagebox.showwarning("warning", "Duplicate values in interest column's values!")
                    mode_window.focus_set()
                    return

            # reinitialize
            self.frac_col_val_to_lbl = {}
            self.frac_col_lbl_to_val = {}
            self.interest_col_val_to_lbl = {}
            self.interest_col_lbl_to_val = {}
            
            # assign values
            if do_select_col.get() == 1.0:
                self.frac_col = combobox_select_col.get()
                for idx, textbox in enumerate(lst_vals_select_col_lbl):
                    if textbox.get("1.0", "end-1c") != "":
                        self.frac_col_val_to_lbl[str(lst_vals_select_col_val[idx].cget('text'))] = str(textbox.get("1.0", "end-1c"))
                        self.frac_col_lbl_to_val[str(textbox.get("1.0", "end-1c"))] = str(lst_vals_select_col_val[idx].cget('text'))
            
            self.interest_col = text_interest_col_create.get("1.0", "end-1c")
            for idx, textbox in enumerate(lst_vals_interest_col_lbl):
                if textbox.get("1.0", "end-1c") != "" and lst_vals_interest_col_val[idx].get("1.0", "end-1c") != "":
                    self.interest_col_val_to_lbl[lst_vals_interest_col_val[idx].get("1.0", "end-1c")] = str(textbox.get("1.0", "end-1c"))
                    self.interest_col_lbl_to_val[str(textbox.get("1.0", "end-1c"))] = lst_vals_interest_col_val[idx].get("1.0", "end-1c")
            self.mode = 'labelizer'
            
        elif combobox_mode.get() == 'correcter':
            # test if nothing missing
            if combobox_interest_col.get() == "Select":
                messagebox.showwarning("warning", "Missing values!")
                mode_window.focus_set()
                return
            lst_values = [str(val) for val in list(self.new_dataset[combobox_interest_col.get()].unique())]
            for idx, textbox in enumerate(lst_vals_interest_col_val):
                if textbox.get("1.0", "end-1c") in lst_values and lst_vals_interest_col_lbl[idx].get("1.0", "end-1c") == "":
                    messagebox.showwarning("warning", "Missing values!")
                    mode_window.focus_set()
                    return
                    
            lst_labels = [textbox.get("1.0", "end-1c") for textbox in lst_vals_interest_col_lbl if textbox.get("1.0", "end-1c") != ""]
            if len(lst_labels) > len(set(lst_labels)):
                    messagebox.showwarning("warning", "Duplicate values in interest column's labels!")
                    mode_window.focus_set()
                    return
            
            # reinitialize
            self.frac_col_val_to_lbl = {}
            self.frac_col_lbl_to_val = {}
            self.interest_col_val_to_lbl = {}
            self.interest_col_lbl_to_val = {}

            # assign values
            self.interest_col = combobox_interest_col.get()
            select_col = combobox_interest_col.get()
            lst_values = self.new_dataset[select_col].unique()
            for idx, textbox in enumerate(lst_vals_interest_col_lbl):
                if textbox.get("1.0", "end-1c") != "" and lst_vals_interest_col_val[idx].get("1.0", "end-1c") != "":
                    self.interest_col_val_to_lbl[lst_values[idx]] = str(textbox.get("1.0", "end-1c"))
                    self.interest_col_lbl_to_val[str(textbox.get("1.0", "end-1c"))] = lst_values[idx]
            self.frac_col = self.interest_col
            self.frac_col_val_to_lbl = {str(val):lbl for val, lbl in self.interest_col_val_to_lbl.items()}
            self.frac_col_lbl_to_val = {lbl:val for val, lbl in self.frac_col_val_to_lbl.items()}
            self.mode = 'correcter'
        else:
            messagebox.showwarning("warning", "Missing values!")
            mode_window.focus_set()
            return

        self.shown_cat = [cat for cat in self.frac_col_val_to_lbl.values()]
        self.num_dataset_to_show = len(self.new_dataset)
        return_value[0] = True
        mode_window.destroy()
    
    # when choosing mode
    def mode_chosen(event):
        mode = combobox_mode.get()
        if mode == 'labelizer':
            toggle_selection_frame(frame_interest_col, 'normal')
            toggle_selection_frame(frame_select_col_header, 'normal')
            combobox_interest_col.set('Select')
            for i in range(6):
                lst_vals_interest_col_val[i].delete("1.0", "end-1c")
                lst_vals_interest_col_val[i].insert("1.0", f"Val {i}")
                lst_vals_interest_col_lbl[i].delete("1.0", "end-1c")
            toggle_selection_frame(frame_interest_col_mapping_sub11 ,'disabled')
            toggle_selection_frame(frame_select_col_mapping ,'disabled')
        else:   # if 'correcter'
            do_select_col.set(0)
            combobox_select_col.set('Select')
            combobox_interest_col.set('Select')
            for i in range(6):
                lst_vals_select_col_val[i].config(text=f"Val {i}", foreground='light grey')
                lst_vals_select_col_lbl[i].delete("1.0", "end-1c")
            text_interest_col_create.delete("1.0","end-1c")
            for i in range(6):
                lst_vals_interest_col_val[i].delete("1.0", "end-1c")
                lst_vals_interest_col_val[i].insert("1.0", f"Val {i}")
                lst_vals_interest_col_val[i].config(foreground='light grey')
                lst_vals_interest_col_lbl[i].delete("1.0", "end-1c")
            toggle_selection_frame(frame_select_col_header, 'disabled')
            toggle_selection_frame(frame_interest_col_mapping_sub2, 'disabled')
            toggle_selection_frame(frame_interest_col_mapping_sub11 ,'normal')
            toggle_selection_frame(frame_interest_col_mapping_sub12 ,'disabled')
            toggle_selection_frame(frame_select_col_mapping ,'disabled')
    
    # when choosing to use a data selection column (two next functions)
    def checkbox_selection_col():
        if do_select_col.get() == 0:
            toggle_selection_frame(frame_select_col_mapping_sub1, 'disabled')
            toggle_selection_frame(frame_select_col_mapping_sub2, 'disabled')
            combobox_select_col.set("Select")
        else:
            toggle_selection_frame(frame_select_col_mapping_sub1, 'normal')

    def toggle_selection_frame(frame, state):
        for child in frame.winfo_children():
            if isinstance(child, (tk.Entry, tk.Label, tk.Button, ttk.Combobox, tk.Checkbutton, tk.Radiobutton, tk.Text)):       
                if state == 'disabled':
                    child.configure(state='disabled', foreground='light grey')
                elif state == 'normal':
                    child.configure(state='normal', foreground='black')
                else:
                    print("problem!")
            elif isinstance(child, tk.Frame):
                toggle_selection_frame(child, state)

    # when selection column of data selection
    def select_col_selection(event):
        select_col = combobox_select_col.get()
        lst_values = self.new_dataset[select_col].unique()
        if len(lst_values) > 6:
            messagebox.showerror("error", "Too many different values for selected column. Max 6 !")
            combobox_select_col.set('Select')
            mode_window.focus_set()
            return
        toggle_selection_frame(frame_select_col_mapping_sub2,'normal')
        for i in range(6):
            lst_vals_select_col_val[i].config(text=f"Val {i}")
            lst_vals_select_col_lbl[i].delete("1.0", "end-1c")
        for idx, value in enumerate(lst_values):
            lst_vals_select_col_val[idx].config(text=value)
        for i in np.arange(len(lst_values), 6):
            lst_vals_select_col_val[i].config(foreground='light grey', state='disabled')
            lst_vals_select_col_lbl[i].config(state='disabled')

    # when selecting the column of interest
    def interest_col_selection(event):
        select_col = combobox_interest_col.get()
        lst_values = self.new_dataset[select_col].unique()
        if len(lst_values) > 6:
            messagebox.showerror("error", "Too many different values for selected column. Max 6 !")
            combobox_interest_col.set('Select')
            mode_window.focus_set()
            return
        toggle_selection_frame(frame_interest_col_mapping_sub2, 'normal')
        
        for i in range(6):
            lst_vals_interest_col_val[i].delete("1.0", "end-1c")
            lst_vals_interest_col_val[i].insert('1.0', f"Val {i}")
            lst_vals_interest_col_lbl[i].delete("1.0", "end-1c")
        for idx, value in enumerate(lst_values):
            lst_vals_interest_col_val[idx].delete("1.0", "end-1c")
            lst_vals_interest_col_val[idx].insert("1.0", value)
            lst_vals_interest_col_val[idx].config(state='disabled')
        mode = combobox_mode.get()
        for i in np.arange(len(lst_values), 6):
            lst_vals_interest_col_val[i].config(foreground='light grey')
            if mode == 'correcter':
                lst_vals_interest_col_val[i].config(state='disabled')
                lst_vals_interest_col_lbl[i].config(state='disabled')

    # move focus to the next widget
    def focus_next(event):
        event.widget.tk_focusNext().focus()
        return "break"  # Prevent the default tab behavior (inserting a tab character)

    # move focus to the previous widget
    def focus_previous(event):
        event.widget.tk_focusPrev().focus()
        return "break"  # Prevent the default tab behavior (inserting a tab character)

    # Function to select all content of a Text widget when it gets focus
    def select_all(event):
        event.widget.focus_set()  # Ensure the widget has focus
        event.widget.tag_add("sel", "1.0", "end-1c")  # Add selection tag
        return "break"  # Prevent default behavior

    # result that say if the mode has been correctly set
    return_value = [False]

    # Retrieve categories from dataset
    if len(self.new_dataset) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        mode_window.destroy()
        return

    # Create a Toplevel window (popup)
    mode_window.title("Categories selection")
    root_pos = [self.root.winfo_x(), self.root.winfo_y()]
    root_dim = [self.root.winfo_width(), self.root.winfo_height()]
    mode_window.geometry(f"400x500+{int(root_pos[0]+root_dim[0]/2-200)}+{int(root_pos[1]+root_dim[1]/2-300)}")

    # select mode
    label = Label(mode_window, text="Select mode:")
    label.pack(anchor='w', padx=10, pady=10)

    combobox_mode = Combobox(mode_window, values=['labelizer', 'correcter'])
    combobox_mode.set("Select an option")  # Texte par défaut
    combobox_mode.pack()

    # select selection column
    #   _ ask if selection column
    frame_select_col_header = Frame(mode_window, width=350, height=30)
    frame_select_col_header.pack(pady=10)
    frame_select_col_header.pack_propagate(False)
    lbl_select_col = Label(frame_select_col_header, text="Do you want to add a selection column?", foreground='light grey', state='disabled')
    lbl_select_col.pack(side='left', padx=10)
    do_select_col = tk.IntVar()
    checkbutton_do_select_col = tk.Checkbutton(frame_select_col_header, text="", variable=do_select_col, onvalue=1, offvalue=0, command=checkbox_selection_col)
    checkbutton_do_select_col.pack(side='right')
    checkbutton_do_select_col.config(state='disabled')
    
    #   _main frame
    frame_select_col = Frame(mode_window, relief=tk.RIDGE, borderwidth=2, width=350, height=130)
    frame_select_col.pack(fill="x", padx=10)
    frame_select_col.pack_propagate(False)

    #   _mapping of the column
    frame_select_col_mapping = Frame(frame_select_col, width=350, height=90)
    frame_select_col_mapping.pack(pady=5)

    #       _column selection
    frame_select_col_mapping_sub1 = Frame(frame_select_col_mapping, width=350, height=30)
    frame_select_col_mapping_sub1.pack()
    frame_select_col_mapping_sub1.pack_propagate(False)
    lbl_select_col_mapping = Label(frame_select_col_mapping_sub1, text="Select column: ", foreground='light grey', state='disabled')
    lbl_select_col_mapping.pack(side='left', padx=10)
    combobox_select_col = Combobox(frame_select_col_mapping_sub1, values=list(self.new_dataset.columns), state="disabled", foreground='light grey')
    combobox_select_col.set("Select")  # Texte par défaut
    combobox_select_col.pack(side='right', padx=10)

    #       _mapping grid
    frame_select_col_mapping_sub2 = Frame(frame_select_col_mapping, width=350, height=60)
    frame_select_col_mapping_sub2.pack()
    lbl_select_grid = Label(frame_select_col_mapping_sub2, text='Map values of column to labels:', state='disabled', foreground='light grey')
    lbl_select_grid.pack(anchor='w')
    lst_vals_select_col_val = []
    lst_vals_select_col_lbl = []
    for i in range(6):
        if not i % 2:
            new_frame = Frame(frame_select_col_mapping_sub2, width=350, height=20)
            new_frame.pack()
            new_frame.pack_propagate(False)
        new_lbl = Label(new_frame, text=f"Val {i}", foreground='light grey', width=5, state='disabled')
        new_lbl.pack(side='left', padx=10)
        new_textbox = Text(new_frame, wrap='none', width=10, height=1)
        new_textbox.pack(side='left', padx=10, expand=False, fill=None)
        new_textbox.config(state='disabled', foreground='light grey')
        new_textbox.bind("<Tab>", focus_next)
        new_textbox.bind("<Return>",  focus_next)
        new_textbox.bind("<Shift-Tab>", focus_previous)
        lst_vals_select_col_val.append(new_lbl)
        lst_vals_select_col_lbl.append(new_textbox)

    #   _select interest column
    frame_interest_col = Frame(mode_window, relief=tk.RIDGE, borderwidth=2, width=350, height=150)
    frame_interest_col.pack(pady=10, padx=10, fill="x")

    #       _mapping of the column
    frame_interest_col_mapping = Frame(frame_interest_col, width=350, height=170)
    frame_interest_col_mapping.pack(pady=5)

    #       _column selection
    frame_interest_col_mapping_sub11 = Frame(frame_interest_col_mapping, width=350, height=30)
    frame_interest_col_mapping_sub11.pack()
    lbl_interest_col_mapping_select = Label(frame_interest_col_mapping_sub11, text="Select column of interest: ", foreground='light grey')
    lbl_interest_col_mapping_select.pack(side='left', padx=10)
    combobox_interest_col = Combobox(frame_interest_col_mapping_sub11, values=list(self.new_dataset.columns), state="disabled", foreground='light grey')
    combobox_interest_col.set("Select")  # Texte par défaut
    combobox_interest_col.pack(side='right', padx=10)
    lbl_random = Label(frame_interest_col_mapping, text='or', state='disabled', foreground='light grey')
    lbl_random.pack()
    frame_interest_col_mapping_sub12 = Frame(frame_interest_col_mapping, width=350, height=30)
    frame_interest_col_mapping_sub12.pack()
    lbl_interest_col_mapping_create = Label(frame_interest_col_mapping_sub12, text="Create column of interest: ", foreground='light grey')
    lbl_interest_col_mapping_create.pack(side='left', padx=10)
    text_interest_col_create = Text(frame_interest_col_mapping_sub12, wrap='none', width=20, height=1, state='disabled', foreground='light grey')
    text_interest_col_create.pack(side='right', padx=10)
    text_interest_col_create.bind("<Tab>", focus_next)
    text_interest_col_create.bind("<Shift-Tab>", focus_previous)
    
    #       _mapping grid
    frame_interest_col_mapping_sub2 = Frame(frame_interest_col_mapping, width=350, height=140)
    frame_interest_col_mapping_sub2.pack()
    lbl_interest_grid = Label(frame_interest_col_mapping_sub2, text='Map values of column to labels:', state='disabled', foreground='light grey')
    lbl_interest_grid.pack(anchor='w')
    lst_vals_interest_col_val = []
    lst_vals_interest_col_lbl = []
    for i in range(6):
        if not i % 2:
            new_frame = Frame(frame_interest_col_mapping_sub2, width=350, height=20)
            new_frame.pack()
            new_frame.pack_propagate(False)
        new_textbox_val = Text(new_frame, wrap='none', width=5, height=1, foreground='light grey')
        new_textbox_val.pack(side='left', padx=10, expand=False, fill=None)
        new_textbox_val.insert("1.0", f"Val {i}")
        new_textbox_val.config(state='disabled')
        new_textbox_lbl = Text(new_frame, wrap='none', width=10, height=1, state='disabled', foreground='light grey')
        new_textbox_lbl.pack(side='left', padx=5, expand=False, fill=None)
        new_textbox_val.bind("<Tab>", focus_next)
        new_textbox_lbl.bind("<Tab>",  focus_next)
        new_textbox_lbl.bind("<Return>",  focus_next)
        new_textbox_val.bind("<Return>",  focus_next)
        new_textbox_val.bind("<Shift-Tab>", focus_previous)
        new_textbox_lbl.bind("<Shift-Tab>",  focus_previous)
        new_textbox_val.bind("<FocusIn>", select_all)
        lst_vals_interest_col_val.append(new_textbox_val)
        lst_vals_interest_col_lbl.append(new_textbox_lbl)

    # Add ok button
    ok_button = ttk.Button(mode_window, text='OK', command=partial(ok_button_pressed, return_value))
    ok_button.pack(pady=15)
    ok_button.bind("<Return>",  partial(ok_button_pressed, return_value))

    # bindings
    combobox_select_col.bind("<<ComboboxSelected>>", select_col_selection)
    combobox_interest_col.bind("<<ComboboxSelected>>", interest_col_selection)
    combobox_mode.bind("<<ComboboxSelected>>", mode_chosen)

    mode_window.wait_window()
    return return_value[0]


def sort_and_filter(self):
    """
    Filters and sorts the dataset based on selected categories and the current sorting configuration.

    Parameters:
        self: object - The instance of the class calling this function.

    Returns:
        DataFrame - A filtered and sorted copy of the dataset.
    """
    shown_cat_keys = [key for key,val in self.frac_col_val_to_lbl.items() if val in self.shown_cat]
    indexes = self.new_dataset.loc[self.new_dataset[self.frac_col].astype('string').isin(shown_cat_keys)].index
    new_df = self.new_dataset.loc[indexes].copy()
    if self.order_var in list(self.new_dataset.columns):
        new_df = new_df.sort_values(
            by=[self.order_var], 
            axis=0, 
            ascending= self.order_asc)
    return new_df


def order(self):
    """
    Opens a window for selecting a sorting criterion and order, then updates the dataset and buffer accordingly.

    Parameters:
        self: object - The instance of the class calling this function.

    Returns:
        None
    """
    def ok_button_pressed(window, combobox, radio_selection):
        if combobox.get() not in list(self.new_dataset.columns):
            messagebox.showwarning("Wrong value", "Wrong ordering value given.")
            default_combobox = "Select an option" if self.order_var == "" else self.order_var
            combobox.set(default_combobox)  # Texte par défaut
            order_window.focus_set()
            return
        self.order_var = combobox.get()
        order = radio_selection.get()
        self.order_asc = order == 'asc'
        self.dataset_to_show = sort_and_filter(self)
        self.buffer.polygons = sort_and_filter(self)
        self.sample_pos = self.dataset_to_show.index.get_loc(self.sample_index)

        # Prepare for buffer reset
        self.buffer.current_pos = self.sample_pos
        self.buffer.current_file_path = ""
        self.original_image = None
        self.display_image = None
        
        # Prepare interface for buffer reset
        set_all_states(self.root, 'disabled', self.menu_bar)

        # Restart buffer
        self.buffer_infos_lbl.config(text="Restarting Temp storages...")
        self.loading_running = True
        threading.Thread(target=thread_restart_buffer, args=[self,]).start()

        window.destroy()

    # Retrieve categories from dataset
    if len(self.new_dataset) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        return
    
    metadatas = list(self.new_dataset.columns)

    # Create a Toplevel window (popup)
    order_window = Toplevel(self.root)
    order_window.title("Categories selection")
    root_pos = [self.root.winfo_x(), self.root.winfo_y()]
    root_dim = [self.root.winfo_width(), self.root.winfo_height()]
    order_window.geometry(f"300x300+{int(root_pos[0]+root_dim[0]/2-150)}+{int(root_pos[1]+root_dim[1]/2-150)}")

    # add label
    label = Label(order_window, text="Select ordering item:")
    label.pack()

    # create the Combobox
    combobox = ttk.Combobox(order_window, values=metadatas)
    default_combobox = "Select an option" if self.order_var == "" else self.order_var
    combobox.set(default_combobox)  # Texte par défaut
    combobox.pack(pady=20)

    # Variable pour stocker la sélection des boutons radio
    radio_selection = tk.StringVar(value="asc" if self.order_asc else "desc")

    # Créer les boutons radio
    radio1 = tk.Radiobutton(order_window, text="Ascending", variable=radio_selection, value="asc")
    radio2 = tk.Radiobutton(order_window, text="Descending", variable=radio_selection, value="desc")

    # Positionner les boutons radio
    radio1.pack()
    radio2.pack()

    # Add ok button
    ok_button = ttk.Button(order_window, text='OK', command=partial(ok_button_pressed, order_window, combobox, radio_selection))
    ok_button.pack()


def open_list_cat(self):
    """
    Opens a window for selecting categories to display in the dataset, updates the dataset, and restarts the buffer.

    Parameters:
        self: object - The instance of the class calling this function.

    Returns:
        None
    """
    def ok_button_pressed(window, tree):
        checked_items = tree.get_checked()

        # Security
        if len(checked_items) == 0:
            messagebox.showwarning("Information", "At least one category must be selected!")
            checkbox_window.focus_set()
            return

        checked_texts = [str(tree.item(item, "text")) for item in checked_items]
        self.shown_cat = checked_texts
        self.dataset_to_show = sort_and_filter(self)
        self.buffer.polygons = sort_and_filter(self)
        self.num_dataset_to_show = len(self.dataset_to_show)

        # If no samples with selection
        if len(self.dataset_to_show) == 0:
            messagebox.showwarning("Information", "With current selection, no samples are available!")
            checkbox_window.focus_set()
            return
        
        # Set new current sample
        if self.sample_index not in list(self.dataset_to_show.index):
            higher_numbers = [x for x in self.dataset_to_show.index if x > self.sample_index]
            self.sample_index = min(higher_numbers) if len(higher_numbers) > 0 else 0
        self.sample_pos = self.dataset_to_show.index.get_loc(self.sample_index)
        
        # Prepare for buffer reset
        self.buffer.current_pos = self.sample_pos
        self.buffer.current_file_path = ""
        self.original_image = None
        self.display_image = None
        
        # Prepare interface for buffer reset
        set_all_states(self.root, 'disabled', self.menu_bar)

        # Restart buffer
        self.buffer_infos_lbl.config(text="Restarting Temp storages...")
        self.loading_running = True
        threading.Thread(target=thread_restart_buffer, args=[self,]).start()

        window.destroy()

    # Retrieve categories from dataset
    if len(self.new_dataset) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        return

    # Create a Toplevel window (popup)
    checkbox_window = Toplevel(self.root)
    checkbox_window.title("Categories selection")
    root_pos = [self.root.winfo_x(), self.root.winfo_y()]
    root_dim = [self.root.winfo_width(), self.root.winfo_height()]
    checkbox_window.geometry(f"300x300+{int(root_pos[0]+root_dim[0]/2-150)}+{int(root_pos[1]+root_dim[1]/2-150)}")

    # add label
    label = Label(checkbox_window, text="Select categories to see:")
    label.pack()

    # create scrollable checkboxes frame
    frame_scrollable = tk.Frame(checkbox_window, width=250, height=200)
    frame_scrollable.pack_propagate(False)
    frame_scrollable.pack(padx=25, pady=10)

    # Add a CheckboxTreeview to the frame
    tree = CheckboxTreeview(frame_scrollable, show="tree")
    tree.pack(side="left", fill="both", expand=True)

    # Add sample items to the CheckboxTreeview
    for lbl in self.frac_col_lbl_to_val.keys():
        if lbl in self.shown_cat:
            tag =('checked')
        else:
            tag = ('unchecked')
        tree.insert("", "end", text=lbl, tags = tag)

    # Add a vertical scrollbar and link it to the CheckboxTreeview
    scrollbar = ttk.Scrollbar(frame_scrollable, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Add ok button
    ok_button = ttk.Button(checkbox_window, text='OK', command=partial(ok_button_pressed, checkbox_window, tree))
    ok_button.pack()


def open_list_meta(self):
    """
    Opens a window for selecting metadata categories to display, updates the dataset, and restarts the buffer.

    Parameters:
        self: object - The instance of the class calling this function.

    Returns:
        None
    """
    def ok_button_pressed(window, tree):
        checked_items = tree.get_checked()
        checked_texts = [tree.item(item, "text") for item in checked_items]
        self.shown_meta = checked_texts
        self.update_infos()
        window.destroy()

    # Retrieve categories from dataset
    if len(self.new_dataset) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        return
    
    metadatas = list(self.new_dataset.columns)

    # Create a Toplevel window (popup)
    checkbox_window = Toplevel(self.root)
    checkbox_window.title("Categories selection")
    root_pos = [self.root.winfo_x(), self.root.winfo_y()]
    root_dim = [self.root.winfo_width(), self.root.winfo_height()]
    checkbox_window.geometry(f"300x300+{int(root_pos[0]+root_dim[0]/2-150)}+{int(root_pos[1]+root_dim[1]/2-150)}")

    # add label
    label = Label(checkbox_window, text="Select categories to see:")
    label.pack()

    # create scrollable checkboxes frame
    frame_scrollable = tk.Frame(checkbox_window, width=250, height=200)
    frame_scrollable.pack_propagate(False)
    frame_scrollable.pack(padx=25, pady=10)

    # Add a CheckboxTreeview to the frame
    tree = CheckboxTreeview(frame_scrollable, show="tree")
    tree.pack(side="left", fill="both", expand=True)

    # Add sample items to the CheckboxTreeview
    for meta in metadatas:
        if meta in self.shown_meta:
            tag =('checked')
        else:
            tag = ('unchecked')
        tree.insert("", "end", text=meta, tags = tag)

    # Add a vertical scrollbar and link it to the CheckboxTreeview
    scrollbar = ttk.Scrollbar(frame_scrollable, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Add ok button
    ok_button = ttk.Button(checkbox_window, text='OK', command=partial(ok_button_pressed, checkbox_window, tree))
    ok_button.pack()


def open_settings(self):
    """
    Opens a settings window for configuring various parameters, validates input, and restarts the buffer if necessary.

    Parameters:
        self: object - The instance of the class calling this function.

    Returns:
        None
    """
    def ok_button_pressed(window, event=None):
        # return
        zooming_max_text = txt_zooming_bound.get("1.0", "end-1c")
        margin_around_image_text = txt_context.get("1.0", "end-1c")
        buffer_front_text = txt_buffer_front.get("1.0", "end-1c")
        buffer_back_text = txt_buffer_back.get("1.0", "end-1c")
        try:
            # Control Zooming
            try:
                zooming_max_text = float(zooming_max_text)
            except Exception as e:
                txt_zooming_bound.delete("1.0", "end-1c")
                raise e
            
            # Control Context
            try:
                margin_around_image_text = int(margin_around_image_text)
            except Exception as e:
                txt_context.delete("1.0", "end-1c")
                raise e

            # Control Buffer
            try:
                buffer_front_text = int(buffer_front_text)
            except Exception as e:
                txt_buffer_front.delete("1.0", "end-1c")
                raise e
            try:
                buffer_back_text = int(buffer_back_text)
            except Exception as e:
                txt_buffer_back.delete("1.0", "end-1c")
                raise e
                
            # Test ranges
            if not 1 <= zooming_max_text <= 10:
                txt_zooming_bound.delete("1.0", "end-1c")
                raise ValueError("Zooming max should be in range [1, 10]")
            if not 0 <= margin_around_image_text <= 1000:
                txt_context.delete("1.0", "end-1c")
                raise ValueError("Margin around image should be in range [0, 1000]")
            if buffer_front_text < 2:
                txt_buffer_front.delete("1.0", "end-1c")
                raise ValueError("Forward In-memory buffer should be higher or equal to 2")
            if buffer_back_text < 2:
                txt_buffer_back.delete("1.0", "end-1c")
                raise ValueError("Backward in-memory should be higher or equal to 2")

        except Exception as e:
            messagebox.showwarning("warning", e)
            Settings_window.focus_set()
            return
        
        # Check if need to restart buffer
        do_restart_buffer = False
        if self.margin_around_image != int(margin_around_image_text) or self.buffer_front_max_size != int(buffer_front_text) or self.buffer_back_max_size != int(buffer_back_text):
            do_restart_buffer = True

        # Update variables
        self.zooming_max = float(zooming_max_text)
        self.drag_prop_to_zoom = bool(do_link_drag_zoom.get())
        self.margin_around_image = int(margin_around_image_text)
        self.buffer_front_max_size = int(buffer_front_text)
        self.buffer_back_max_size = int(buffer_back_text)

        # Restart buffer if necessary and update
        if self.buffer and do_restart_buffer:# Restart buffer
            # Prepare interface for buffer reset
            set_all_states(self.root, 'disabled', self.menu_bar)

            # Restart buffer
            self.buffer_infos_lbl.config(text="Restarting Temp storages...")
            self.loading_running = True
            threading.Thread(target=thread_restart_buffer, args=[self,]).start()
        else:
            self.update_infos()

        window.destroy()


    # Create a Toplevel window (popup)
    Settings_window = Toplevel(self.root)
    Settings_window.title("Settings")
    root_pos = [self.root.winfo_x(), self.root.winfo_y()]
    root_dim = [self.root.winfo_width(), self.root.winfo_height()]
    Settings_window.geometry(f"300x300+{int(root_pos[0]+root_dim[0]/2-200)}+{int(root_pos[1]+root_dim[1]/2-150)}")

    # Zooming part
    frame_zooming = Frame(Settings_window, relief=tk.RIDGE, borderwidth=2, width=280, height=60)
    frame_zooming.pack(pady=10, padx=10)
    frame_zooming.pack_propagate(False)

    #   _zooming boundary
    frame_zooming_bound = Frame(frame_zooming, width=280, height=30,)
    frame_zooming_bound.pack()
    frame_zooming_bound.pack_propagate(False)
    lbl_zooming_bound = Label(frame_zooming_bound, text="Zooming max :", width=18, justify='left', anchor='w')
    lbl_zooming_bound.pack(side="left", padx=10, anchor='w')
    txt_zooming_bound = Text(frame_zooming_bound, wrap='none', width=4, height=1)
    txt_zooming_bound.pack(side="right", padx=30)
    txt_zooming_bound.insert("1.0", str(self.zooming_max))
    txt_zooming_bound.bind("<Return>",  partial(ok_button_pressed, Settings_window))

    #   _zooming drag linked to zoom
    frame_zooming_drag = Frame(frame_zooming, width=280, height=30)
    frame_zooming_drag.pack()
    frame_zooming_drag.pack_propagate(False)
    lbl_zooming_drag = Label(frame_zooming_drag, text="Drag speed linked to zoom :", width=20, justify='left', anchor='w')
    lbl_zooming_drag.pack(side="left", padx=10, anchor='w')
    do_link_drag_zoom = tk.IntVar(value=int(self.drag_prop_to_zoom))
    cb_zooming_drag = Checkbutton(frame_zooming_drag, text="", variable=do_link_drag_zoom)
    cb_zooming_drag.pack(side='right', padx=30)

    # Context part
    frame_context = Frame(Settings_window, relief=tk.RIDGE, borderwidth=2, width=280, height=40)
    frame_context.pack(pady=10)
    frame_context.pack_propagate(False)
    lbl_context = Label(frame_context, text="Margin around image :", width=18, justify='left', anchor='w')
    lbl_context.pack(side='left', padx=10)
    txt_context = Text(frame_context, wrap='none', width=4, height=1)
    txt_context.pack(side="right", padx=30)
    txt_context.insert("1.0", str(self.margin_around_image))
    txt_context.bind("<Return>",  partial(ok_button_pressed, Settings_window))

    # Buffer part
    frame_buffer = Frame(Settings_window, relief=tk.RIDGE, borderwidth=2, width=280, height=90)
    frame_buffer.pack(pady=10)
    frame_buffer.pack_propagate(False)
    lbl_buffer_1 = Label(frame_buffer, text='In-memory sizes: ', justify='left', anchor='w', width=200)
    lbl_buffer_1.pack(padx=10)
    
    #   _front buffer
    frame_buffer_front = Frame(frame_buffer, width=280, height=30)
    frame_buffer_front.pack()
    frame_buffer_front.pack_propagate(False)
    lbl_buffer_front = Label(frame_buffer_front, text='\t     - forward :', justify='right', anchor='w', width=20)
    lbl_buffer_front.pack(side='left', padx=10)
    txt_buffer_front = Text(frame_buffer_front, wrap='none', width=4, height=1)
    txt_buffer_front.pack(side='right', padx=30)
    txt_buffer_front.insert("1.0", str(self.buffer_front_max_size))
    txt_buffer_front.bind("<Return>",  partial(ok_button_pressed, Settings_window))

    #   _back buffer
    frame_buffer_back = Frame(frame_buffer, width=280, height=30)
    frame_buffer_back.pack()
    frame_buffer_back.pack_propagate(False)
    lbl_buffer_back = Label(frame_buffer_back, text='\t     - backward :', justify='left', anchor='w', width=20)
    lbl_buffer_back.pack(side='left', padx=10)
    txt_buffer_back = Text(frame_buffer_back, wrap='none', width=4, height=1)
    txt_buffer_back.pack(side='right', padx=30)
    txt_buffer_back.insert("1.0", str(self.buffer_back_max_size))
    txt_buffer_back.bind("<Return>",  partial(ok_button_pressed, Settings_window))

    # OK button
    ok_button = ttk.Button(Settings_window, text='OK', command=partial(ok_button_pressed, Settings_window))
    ok_button.pack()
