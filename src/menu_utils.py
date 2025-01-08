import tkinter as tk
import os
import numpy as np
import pickle
import rasterio
import pandas as pd
from time import sleep, time
from tkinter import Tk, Menu, Label, Button, Frame, Text, font, filedialog, messagebox, Checkbutton, Scrollbar, IntVar, Canvas,Toplevel
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
from tkinter.ttk import Combobox
from ttkwidgets import CheckboxTreeview
import geopandas as gpd
from functools import partial
import threading


import sys
sys.path.insert(0,'D:\GitHubProjects\STDL_sample_labelizer')
from src.processing import show_confusion_matrix
from src.buffer import Buffer


def menu_mode_choice(self, mode_window):
    def ok_button_pressed(return_value):
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


def load(self, mode=0):
    def start_buffer():
        try:
            if self.buffer:
                self.buffer.purge()
        finally:
            try:
                self.buffer = Buffer(
                    rasters_src=self.raster_path,
                    polygons=self.dataset_to_show,
                    margin_around_image=self.margin_around_image,
                    buffer_front_max_size=self.buffer_front_max_size,
                    buffer_back_max_size=self.buffer_back_max_size,
                )
                self.buffer.current_pos = self.sample_pos
                self.buffer.start()
                self.show_image()
            except Exception as e:
                print("An error occured while initiating buffer: ", e)
            finally:
                # Activate navigation buttons
                set_all_states(self.root, 'normal', self.menu_bar)
                self.loading_running = False
                self.buffer_infos_lbl.config(text="")

    # test if ongoing unsaved project
    if self.UnsavedChanges == True:
        result = messagebox.askyesnocancel("Confirmation", "There is unsaved changes! Do you want to save?")
        if result == True:
            save(self)
        elif result == False:
            pass
        else:
            return

    # load polygon
    if mode in [0,1]:
        self.polygon_path = filedialog.askopenfilename(
        title="Select the vector source",
        filetypes=[("GeoPackage Files", "*.gpkg"), ("All Files", "*.*")]
        )
        if self.polygon_path != "":
            self.dataset = gpd.read_file(self.polygon_path)
            self.new_dataset = gpd.read_file(self.polygon_path)
            self.old_crs = self.dataset.crs
            
            # verify if a save already exists
            new_polygon_path = self.polygon_path.split('.')[:-1]
            new_polygon_path.append("_corrected")
            new_polygon_path = ''.join(new_polygon_path)
            if os.path.exists(new_polygon_path):
                if messagebox.askyesno("Save found", "A save already exists for this file. Do you want to continue from it?"):
                    try:
                        with open(os.path.join(new_polygon_path, 'save_file.pkl'), 'rb') as in_file:
                            dict_save = pickle.load(in_file)
                        self.polygon_path = dict_save['polygon_path']
                        self.raster_path = dict_save['raster_path']
                        self.dataset = dict_save['dataset']
                        self.new_dataset = dict_save['new_dataset']
                        self.dataset_to_show = dict_save['dataset_to_show']
                        self.new_crs = dict_save['new_crs']
                        self.old_crs = dict_save['old_crs']
                        self.sample_index = dict_save['sample_index']
                        self.sample_pos = dict_save['sample_pos']
                        self.shown_cat = dict_save['shown_cat']
                        self.shown_meta = dict_save['shown_meta']
                        self.list_rasters_src = dict_save['list_rasters_src']
                        self.mode = dict_save['mode']
                        self.frac_col = dict_save['frac_col']
                        self.interest_col = dict_save['interest_col']
                        self.frac_col_lbl_to_val = dict_save['frac_col_lbl_to_val']
                        self.frac_col_val_to_lbl = dict_save['frac_col_val_to_lbl']
                        self.interest_col_lbl_to_val = dict_save['interest_col_lbl_to_val']
                        self.interest_col_val_to_lbl = dict_save['interest_col_val_to_lbl']
                        self.changes_log = dict_save['changes_log']
                    except Exception as e:
                        print("An error occured. The save file \"save_file.pkl\" must be absent or corrupted.")
                        print(f"Original error: {e}")
                    mode = -1
            if mode != -1:
                # reset variables
                self.changes_log = []
                self.shown_cat = []
                self.shown_meta = []
                self.order_var = None
                self.order_asc = True

                # show mode choice window
                top_level = Toplevel(self.root)
                is_mode_well_set =  menu_mode_choice(self, top_level)
                if not is_mode_well_set: # make sure that the polygon is well set
                    return
                
                # continue to process input polygons
                if self.mode == 'labelizer':
                    """self.new_dataset.rename(columns={self.frac_col:'class_binary'}, inplace=True)
                    self.frac_col = 'class_binary'
                    self.new_dataset.class_binary = self.new_dataset.class_binary.astype('string')
                    for cat, val in self.frac_col_lbl_to_val.items():
                        self.new_dataset.loc[self.new_dataset.class_binary == str(val), 'class_binary'] = str(cat)"""
                    self.new_dataset[self.interest_col] = ""
                self.dataset_to_show = self.new_dataset.copy()

    # load rasters
    if mode in [0,2]:
        self.raster_path = filedialog.askdirectory(title="Select the raster source")
        if self.raster_path != '':
            self.list_rasters_src = []
            for r, d, f in os.walk(self.raster_path):
                for file in f:
                    if file.endswith('.tif'):
                        file_src = r + '/' + file
                        file_src = file_src.replace('\\','/')
                        self.list_rasters_src.append(file_src)
            # find crs
            if len(self.list_rasters_src) > 0:
                with rasterio.open(self.list_rasters_src[0], 'r') as raster:
                    self.new_crs = raster.crs

    if mode == 3:
        save_path = filedialog.askopenfilename(
        title="Select the save file",
        filetypes=[("Pickle Files", "*.pkl *.pickle"), ("All Files", "*.*")]
        )

        if save_path != "":
            try:
                with open(os.path.join(save_path), 'rb') as in_file:
                    dict_save = pickle.load(in_file)
                self.polygon_path = dict_save['polygon_path']
                self.raster_path = dict_save['raster_path']
                self.dataset = dict_save['dataset']
                self.new_dataset = dict_save['new_dataset']
                self.dataset_to_show = dict_save['dataset_to_show']
                self.new_crs = dict_save['new_crs']
                self.old_crs = dict_save['old_crs']
                self.sample_index = dict_save['sample_index']
                self.sample_pos = dict_save['sample_pos']
                self.shown_cat = dict_save['shown_cat']
                self.shown_meta = dict_save['shown_meta']
                self.list_rasters_src = dict_save['list_rasters_src']
                self.mode = dict_save['mode']
                self.frac_col = dict_save['frac_col']
                self.interest_col = dict_save['interest_col']
                self.frac_col_lbl_to_val = dict_save['frac_col_lbl_to_val']
                self.frac_col_val_to_lbl = dict_save['frac_col_val_to_lbl']
                self.interest_col_lbl_to_val = dict_save['interest_col_lbl_to_val']
                self.interest_col_val_to_lbl = dict_save['interest_col_val_to_lbl']
                self.changes_log = dict_save['changes_log']
            except Exception as e:
                print("An error occured. The save file \"save_file.pkl\" must be absent or corrupted.")
                print(f"Original error: {e}")

    if self.polygon_path != "" and self.raster_path != "":
        # Attriute new crs
        self.new_dataset = self.new_dataset.to_crs(crs=self.new_crs)
        self.dataset_to_show = self.dataset_to_show.to_crs(crs=self.new_crs)

        # Reset categorie buttons (if loading from former project)
        for i in range(6):
            self.lst_buttons_category[i].config(text='-', state='disabled')

        # Activate categorie buttons
        for idx, (val, label) in enumerate(self.interest_col_val_to_lbl.items()):
            label = label[0:13] + '..' if len(label) > 15 else label
            self.lst_buttons_category[idx].config(text=label, state='normal')
            self.attribute_button_command(self.lst_buttons_category[idx], val)
        
        # Initiate buffer
        try:
            set_all_states(self.root, 'disabled', self.menu_bar)
            self.buffer_infos_lbl.config(text="Initialising buffer...")
            self.loading_running = True
            threading.Thread(target=start_buffer).start()
        finally:
            self.update_infos()
            self.do_autosave = True
            self.auto_save()

    elif self.polygon_path != "" or self.raster_path != "":
        self.update_infos()
    

def save(self, verbose=True):
    # if self.UnsavedChanges == 0:
    #     _ = messagebox.showinfo("Information", "No changes has been detected.")
    #     return

    # create new gpgk file
    try:
        # create folder
        new_polygon_path = self.polygon_path.split('.')[:-1]
        new_polygon_path.append("_corrected")
        new_polygon_path = ''.join(new_polygon_path)
        if not os.path.exists(new_polygon_path):
            os.mkdir(new_polygon_path)

        # create geopackage file
        new_name = new_polygon_path.split('/')[-1]
        new_polygon_name = new_name + ".gpkg"
        new_polygon_name = ''.join(new_polygon_name)
        new_csv_name = new_name + ".csv"
        new_csv_name = ''.join(new_csv_name)
        new_polygon_src = os.path.join(new_polygon_path, new_polygon_name)
        new_csv_src = os.path.join(new_polygon_path, new_csv_name)

        # save dataset to geopackage and csv
        if self.mode == 'labelizer':
            self.new_dataset.loc[self.new_dataset[self.interest_col] != ""].drop('geometry', axis=1).to_csv(new_csv_src, sep=';', index=None)
            self.new_dataset.loc[self.new_dataset[self.interest_col] != ""].to_crs(self.old_crs).to_file(new_polygon_src)
        else: # if self.mode  = 'correcter
            self.new_dataset.to_crs(self.old_crs).to_file(new_polygon_src)
            self.new_dataset.drop('geometry', axis=1).to_csv(new_csv_src, sep=';', index=None)

        # save list of changes
        with open(os.path.join(new_polygon_path, 'modification_logs.txt'), 'w') as file:
            for change in self.changes_log:
                file.write(f"{change}\n")

        # save GeoDataFrames
        dict_save = {
            'polygon_path': self.polygon_path,
            'raster_path': self.raster_path,
            'dataset': self.dataset,
            'new_dataset': self.new_dataset,
            'dataset_to_show': self.dataset_to_show,
            'new_crs': self.new_crs,
            'old_crs': self.old_crs,
            'sample_index': self.sample_index,
            'sample_pos': self.sample_pos,
            'shown_cat': self.shown_cat,
            'shown_meta': self.shown_meta,
            'list_rasters_src': self.list_rasters_src,
            'mode': self.mode,
            'frac_col': self.frac_col,
            'interest_col': self.interest_col,
            'frac_col_lbl_to_val': self.frac_col_lbl_to_val,
            'frac_col_val_to_lbl': self.frac_col_val_to_lbl,
            'interest_col_lbl_to_val': self.interest_col_lbl_to_val,
            'interest_col_val_to_lbl': self.interest_col_val_to_lbl,
            'changes_log': self.changes_log,
        }
        with open(os.path.join(new_polygon_path, 'save_file.pkl'),'wb') as out_file:
            pickle.dump(dict_save, out_file)

    except AttributeError:
        _ = messagebox.showerror("Error", "A problem happened! Either the path to the polygon has not been set or is non-existant.")
    else:
        if verbose:
            _ = messagebox.showinfo("Information", f"The changes have been saved in folder :\n{new_polygon_path}")
        self.UnsavedChanges = False

        # compute visualization of data analysis
        # if self.mode == 'correcter':
        #     dict_char_to_num = {'b':0,'t':1,'s':2,'e':3,'l':4,'i':5}
        #     pred_dataset = self.dataset.loc[list(self.new_dataset.index)]
        #     true = [dict_char_to_num[x] for x in list(self.new_dataset['class'].values)]
        #     pred = [dict_char_to_num[x] for x in list(pred_dataset['class'].values)]
        #     show_confusion_matrix(
        #         y_pred=pred,
        #         y_true=true,
        #         target_src=os.path.join(new_polygon_path, 'performances.png'),
        #         class_labels=self.frac_col_lbl_to_val.values(),
        #         title="Performances",
        #         do_save=True,
        #         do_show=False,
        #     )


def exit(self):
    # Check if program processing
    if self.loading_running:
        messagebox.showwarning("Process running", "Please, wait for the running processes to finish before quitting.")
        return
    
    # Check if unsaved changes
    if self.UnsavedChanges == True:
        result = messagebox.askyesnocancel("Confirmation", "There is unsaved changes! Do you want to save?")
        if result == True:
            save(self)
        elif result == False:
            pass
        else:
            return
    
    # Purge the buffer before quitting
    if self.buffer:
        self.buffer.purge()

    self.root.quit()


def sort_and_filter(self):
    shown_cat_keys = [key for key,val in self.frac_col_val_to_lbl.items() if val in self.shown_cat]
    indexes = self.new_dataset.loc[self.new_dataset[self.frac_col].astype('string').isin(shown_cat_keys)].index
    new_df = self.new_dataset.loc[indexes].copy()
    if self.order_var != "":
        new_df = new_df.sort_values(
            by=[self.order_var], 
            axis=0, 
            ascending= self.order_asc)
    return new_df


def thread_restart_buffer(self, mode='restart'):
    # Reset buffer and then update shown infos
    try:
        self.buffer.restart(self.buffer_front_max_size, self.buffer_back_max_size, self.margin_around_image)
    except Exception as e:
        print("An error occured while restarting buffer: ", e)
        try:
            save(self)
            print("For safety measures, the current state of the work was saved.")
        except Exception as e:
            print("During the management of the error, the program tried to save the work but did not manage due to the following error", e)
        
    finally:
        self.loading_running = False
        self.update_infos()
        self.show_image()
        self.buffer_infos_lbl.config(text="")
        set_all_states(self.root, 'normal', self.menu_bar)


def set_all_states(parent, state, menu=None):
    for child in parent.winfo_children():
        if isinstance(child, (ttk.Button, Text, ttk.Combobox)):
            child.config(state=state)
        elif isinstance(child, Frame):
            set_all_states(child, state)
    if menu:   
        for i in range(menu.index('end') + 1):  # Iterate through all items
            menu.entryconfig(i, state=state)


def order(self):
    def ok_button_pressed(window, combobox, radio_selection):
        if combobox.get() == "Select an option":
            window.destroy()
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
        self.buffer_infos_lbl.config(text="Restarting buffer...")
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
    default_combobox = "Select an option" if self.order_var == None else self.order_var
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
    def ok_button_pressed(window, tree):
        checked_items = tree.get_checked()

        # Security
        if len(checked_items) == 0:
            messagebox.showwarning("Information", "At least one category must be selected!")
            return

        checked_texts = [str(tree.item(item, "text")) for item in checked_items]
        self.shown_cat = checked_texts
        self.dataset_to_show = sort_and_filter(self)
        self.buffer.polygons = sort_and_filter(self)
        self.num_dataset_to_show = len(self.dataset_to_show)

        # If no samples with selection
        if len(self.dataset_to_show) == 0:
            messagebox.showwarning("Information", "With current selection, no samples are available!")
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
        self.buffer_infos_lbl.config(text="Restarting buffer...")
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
    def ok_button_pressed(window, event=None):
        # print(do_link_drag_zoom.get())
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
                raise ValueError("Front buffer should be higher or equal to 2")
            if buffer_back_text < 2:
                txt_buffer_back.delete("1.0", "end-1c")
                raise ValueError("Back buffer should be higher or equal to 2")

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
            self.buffer_infos_lbl.config(text="Restarting buffer...")
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
    lbl_zooming_drag = Label(frame_zooming_drag, text="Drag linked to zoom :", width=20, justify='left', anchor='w')
    lbl_zooming_drag.pack(side="left", padx=10, anchor='w')
    do_link_drag_zoom = tk.IntVar(value=int(self.drag_prop_to_zoom))
    cb_zooming_drag = Checkbutton(frame_zooming_drag, text="", variable=do_link_drag_zoom)
    cb_zooming_drag.pack(side='right', padx=30)

    # Context part
    frame_context = Frame(Settings_window, relief=tk.RIDGE, borderwidth=2, width=280, height=40)
    frame_context.pack(pady=10)
    frame_context.pack_propagate(False)
    lbl_context = Label(frame_context, text="Context size :", width=18, justify='left', anchor='w')
    lbl_context.pack(side='left', padx=10)
    txt_context = Text(frame_context, wrap='none', width=4, height=1)
    txt_context.pack(side="right", padx=30)
    txt_context.insert("1.0", str(self.margin_around_image))
    txt_context.bind("<Return>",  partial(ok_button_pressed, Settings_window))

    # Buffer part
    frame_buffer = Frame(Settings_window, relief=tk.RIDGE, borderwidth=2, width=280, height=90)
    frame_buffer.pack(pady=10)
    frame_buffer.pack_propagate(False)
    lbl_buffer_1 = Label(frame_buffer, text='Buffer sizes: ', justify='left', anchor='w', width=200)
    lbl_buffer_1.pack(padx=10)
    
    #   _front buffer
    frame_buffer_front = Frame(frame_buffer, width=280, height=30)
    frame_buffer_front.pack()
    frame_buffer_front.pack_propagate(False)
    lbl_buffer_front = Label(frame_buffer_front, text='\t     - front :', justify='right', anchor='w', width=20)
    lbl_buffer_front.pack(side='left', padx=10)
    txt_buffer_front = Text(frame_buffer_front, wrap='none', width=4, height=1)
    txt_buffer_front.pack(side='right', padx=30)
    txt_buffer_front.insert("1.0", str(self.buffer_front_max_size))
    txt_buffer_front.bind("<Return>",  partial(ok_button_pressed, Settings_window))

    #   _back buffer
    frame_buffer_back = Frame(frame_buffer, width=280, height=30)
    frame_buffer_back.pack()
    frame_buffer_back.pack_propagate(False)
    lbl_buffer_back = Label(frame_buffer_back, text='\t     - back :', justify='left', anchor='w', width=20)
    lbl_buffer_back.pack(side='left', padx=10)
    txt_buffer_back = Text(frame_buffer_back, wrap='none', width=4, height=1)
    txt_buffer_back.pack(side='right', padx=30)
    txt_buffer_back.insert("1.0", str(self.buffer_back_max_size))
    txt_buffer_back.bind("<Return>",  partial(ok_button_pressed, Settings_window))

    # OK button
    ok_button = ttk.Button(Settings_window, text='OK', command=partial(ok_button_pressed, Settings_window))
    ok_button.pack()


def remove_sample(self):
    # verify if polygon loaded
    if len(self.new_dataset) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        return

    # Remove sample
    self.dataset_to_show = self.dataset_to_show.drop(self.sample_index, axis=0)
    self.new_dataset = self.new_dataset.drop(self.sample_index, axis=0)
    
    # Update current sample
    self.sample_pos = (self.sample_pos + 1) % len(self.dataset_to_show)
    self.sample_index = self.dataset_to_show.index[self.sample_pos]

    # Add in corresponding list for potential retrieval
    self.changes_log.append("removing " + str(self.sample_index))
    
    # Remove from buffer
    self.original_image = None
    self.display_image = None
    try:
        self.buffer.delete_sample()
    finally:
        self.UnsavedChanges = True
        self.update_infos()
        self.show_image()


if __name__ == '__main__':
    """polygon_path = "D:/GitHubProjects/STDL_Classifier/data/sources/gt_MNC_filtered.gpkg"
    data = gpd.read_file(polygon_path)
    data.drop('geometry', axis=1).to_csv("D:/GitHubProjects/STDL_Classifier/data/sources/gt_MNC_filtered_corrected/gt_MNC_filtered.gpkg.csv", sep=';', index=None)"""
    # lst = ['a', 'b', 'c']
    # lst.remove('a')
    # print(lst)
    pass

