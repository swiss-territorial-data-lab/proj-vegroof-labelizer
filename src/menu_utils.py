import tkinter as tk
import os
import numpy as np
import pickle
import pandas as pd
from tkinter import Tk, Menu, Label, Button, Frame, Text, font, filedialog, messagebox, Checkbutton, Scrollbar, IntVar, Canvas,Toplevel
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
from tkinter.ttk import Combobox
from ttkwidgets import CheckboxTreeview
import geopandas as gpd
from functools import partial
from src.processing import show_confusion_matrix


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

            # assign values
            if do_select_col.get() == 1.0:
                self.frac_col = combobox_select_col.get()
                for idx, textbox in enumerate(lst_vals_select_col_lbl):
                    if textbox.get("1.0", "end-1c") != "":
                        self.frac_col_val_to_lbl[lst_vals_select_col_val[idx].cget('text')] = str(textbox.get("1.0", "end-1c"))
                        self.frac_col_lbl_to_val[str(textbox.get("1.0", "end-1c"))] = lst_vals_select_col_val[idx].cget('text')
            
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
            
            # assign values
            self.interest_col = combobox_interest_col.get()
            select_col = combobox_interest_col.get()
            lst_values = self.new_dataset[select_col].unique()
            for idx, textbox in enumerate(lst_vals_interest_col_lbl):
                if textbox.get("1.0", "end-1c") != "" and lst_vals_interest_col_val[idx].get("1.0", "end-1c") != "":
                    #self.interest_col_val_to_lbl[lst_vals_interest_col_val[idx].get("1.0", "end-1c")] = str(textbox.get("1.0", "end-1c"))
                    #self.interest_col_lbl_to_val[str(textbox.get("1.0", "end-1c"))] = lst_vals_interest_col_val[idx].get("1.0", "end-1c")
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

        #self.new_dataset = self.new_dataset.loc[self.new_dataset[self.frac_col].isin(list(self.frac_col_lbl_to_val.keys()))]
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
    label.pack(anchor='w', padx=10)

    combobox_mode = Combobox(mode_window, values=['labelizer', 'correcter'])
    combobox_mode.set("Select an option")  # Texte par défaut
    combobox_mode.pack(pady=20)

    # select selection column
    #   _ ask if selection column
    frame_select_col_header = Frame(mode_window, width=350, height=30)
    frame_select_col_header.pack()
    frame_select_col_header.pack_propagate(False)
    lbl_select_col = Label(frame_select_col_header, text="Do you want to add a selection column?", foreground='light grey', state='disabled')
    lbl_select_col.pack(side='left', padx=10)
    do_select_col = tk.IntVar()
    checkbutton_do_select_col = tk.Checkbutton(frame_select_col_header, text="", variable=do_select_col, onvalue=1, offvalue=0, command=checkbox_selection_col)
    checkbutton_do_select_col.pack(side='right')
    checkbutton_do_select_col.config(state='disabled')
    
    #   _main frame
    frame_select_col = Frame(mode_window, width=350, height=150)
    frame_select_col.pack()
    frame_select_col.pack_propagate(False)

    #   _mapping of the column
    frame_select_col_mapping = Frame(frame_select_col, width=350, height=90)
    frame_select_col_mapping.pack()

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
        new_textbox = Text(new_frame, width=10, height=1)
        new_textbox.pack(side='left', padx=10, expand=False, fill=None)
        new_textbox.config(state='disabled', foreground='light grey')
        lst_vals_select_col_val.append(new_lbl)
        lst_vals_select_col_lbl.append(new_textbox)

    # select interest column
    frame_interest_col = Frame(mode_window, width=350, height=150)
    frame_interest_col.pack()

    #   _mapping of the column
    frame_interest_col_mapping = Frame(frame_interest_col, width=350, height=170)
    frame_interest_col_mapping.pack()

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
    text_interest_col_create = Text(frame_interest_col_mapping_sub12, width=20, height=1, state='disabled', foreground='light grey')
    text_interest_col_create.pack(side='right', padx=10)

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
        new_textbox_val = Text(new_frame, width=5, height=1, foreground='light grey')
        new_textbox_val.pack(side='left', padx=10, expand=False, fill=None)
        new_textbox_val.insert("1.0", f"Val {i}")
        new_textbox_val.config(state='disabled')
        new_textbox_lbl = Text(new_frame, width=10, height=1, state='disabled', foreground='light grey')
        new_textbox_lbl.pack(side='left', padx=5, expand=False, fill=None)
        lst_vals_interest_col_val.append(new_textbox_val)
        lst_vals_interest_col_lbl.append(new_textbox_lbl)

    # Add ok button
    ok_button = ttk.Button(mode_window, text='OK', command=partial(ok_button_pressed, return_value))
    ok_button.pack(pady=20)

    # bindings
    combobox_select_col.bind("<<ComboboxSelected>>", select_col_selection)
    combobox_interest_col.bind("<<ComboboxSelected>>", interest_col_selection)
    combobox_mode.bind("<<ComboboxSelected>>", mode_chosen)

    mode_window.wait_window()
    return return_value[0]


def menu_mode_choice_2(self, mode_window):
    def toggle_enabled(cbb:Combobox, lbls:list, value):
        cbb.config(state=value)
        if cbb['state'] == 'enabled':
            cbb.configure(foreground='black')
            for lbl in lbls:
                lbl.config(fg='black')
        else:
            cbb.configure(foreground='light grey')
            for lbl in lbls:
                lbl.config(fg='light grey')

    def ok_button_pressed(return_value):
        pool_of_multi_labels = {'b':'bare', 't':'terrace', 's':'spontaneous', 'e':'extensive', 'l':'lawn', 'i':'intensive'}
        if combobox_mode.get() != 'Select and option' and combobox_class != 'Select an option':
            self.mode = combobox_mode.get()
            self.frac_col = combobox_class.get()
            self.new_dataset[self.frac_col] = self.new_dataset[self.frac_col]
            if combobox_bare.get() != '-' and combobox_vege.get() != '-' and self.mode == 'labelizer':
                self.frac_col_lbl_to_val = {
                    combobox_bare.get(): 'bare',
                    combobox_vege.get(): 'vegetated',
                }
                self.class_to_label = {val:key for key,val in self.frac_col_lbl_to_val.items()}
            elif self.mode == 'correcter':
                self.frac_col_lbl_to_val = {x:y for x,y in pool_of_multi_labels.items() if x in self.new_dataset[self.frac_col].unique()}
                self.class_to_label = {val:key for key,val in self.frac_col_lbl_to_val.items()}
            else:
                mode_window.destroy()
                return
            
            self.new_dataset = self.new_dataset.loc[self.new_dataset[self.frac_col].isin(list(self.frac_col_lbl_to_val.keys()))]
            
            self.shown_cat = [str(val) for val in self.frac_col_lbl_to_val.values()]
            return_value[0] = True
            mode_window.destroy()
    
    def mode_chosen(event):
        mode = combobox_mode.get()
        if mode in ['labelizer', 'correcter']:
            toggle_enabled(combobox_class, [lbl_class_name], 'enabled')
            if combobox_class.get() != 'Select an option':
                class_chosen(event)
            if mode == 'correcter':
                toggle_enabled(combobox_bare, [lbl_mapping, lbl_bare], 'disabled')
                toggle_enabled(combobox_vege, [lbl_vege], 'disabled')
                combobox_bare.set('-')
                combobox_vege.set('-')
                mapping_classes(event)
        else:
            print('no mode selected!')

    def class_chosen(event):  
        class_name = combobox_class.get()
        class_values = list(self.new_dataset[class_name].unique())
        mode = combobox_mode.get()

        if mode == 'labelizer':
            if len(class_values) > 2:
                messagebox.showwarning("warning", "The number of different values is greater than 2. After choosing the one corresponding to bare and vegetation samples, the samples with other values will be dismissed!")
                mode_window.focus_set()

            # set mapping
            combobox_bare.config(state='enabled', values=class_values)
            combobox_vege.config(state='enabled', values=class_values)
            toggle_enabled(combobox_bare, [lbl_mapping, lbl_bare], 'enabled')
            toggle_enabled(combobox_vege, [lbl_vege], 'enabled')
        elif mode == 'correcter':
            pool_of_multi_labels = set(['b', 't', 's', 'e', 'l', 'i'])
            if set(class_values).intersection(pool_of_multi_labels) == set([]):
                messagebox.showerror("error", "The values of the class don't match the ones for multi class!")
                mode_window.focus_set()
                return
            elif set(class_values).intersection(pool_of_multi_labels) != set(class_values):
                messagebox.showwarning("error", "Some of the values of the class don't match the ones for multi class! Cooresponding samples will not be kept")
                mode_window.focus_set()
            ok_button.config(state='enabled')
        else:
            print('no class name selected!')

    def mapping_classes(event):
        bare_value = combobox_bare.get()
        vege_value = combobox_vege.get()
        if bare_value != '-' and vege_value != '-' and bare_value != vege_value:
            ok_button.config(state='enabled')
        else:
            ok_button.config(state='disabled')

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
    mode_window.geometry(f"300x350+{int(root_pos[0]+root_dim[0]/2-150)}+{int(root_pos[1]+root_dim[1]/2-300)}")

    # select mode
    label = Label(mode_window, text="Select mode:")
    label.pack(anchor='w', padx=10)

    combobox_mode = Combobox(mode_window, values=['labelizer', 'correcter'])
    combobox_mode.set("Select an option")  # Texte par défaut
    combobox_mode.pack(pady=20)

    # select label column
    lbl_class_name = Label(mode_window, text="Select the column with the class name:", fg='light grey')
    lbl_class_name.pack(anchor='w', padx=10)

    combobox_class = Combobox(mode_window, values=list(self.new_dataset.columns))
    combobox_class.set("Select an option")  # Texte par défaut
    combobox_class.pack(pady=20)
    combobox_class.config(state="disabled", foreground='light grey')

    # map label to class
    lbl_mapping = Label(mode_window, text='Values mapping (only in "labelizer" mode):', fg='light grey')
    lbl_mapping.pack(anchor='w', padx=10)

    frame_bare = Frame(mode_window, width=250, height=35)
    frame_bare.pack()
    frame_bare.pack_propagate(False) 
    lbl_bare = Label(frame_bare, text='bare: ', fg='light grey')
    lbl_bare.pack(side='left')
    combobox_bare = Combobox(frame_bare, values=range(4), width=15)
    combobox_bare.set('-')  # Texte par défaut
    combobox_bare.pack(side='right')
    combobox_bare.config(state="disabled", foreground='light grey')

    frame_vege = Frame(mode_window, width=250, height=35)
    frame_vege.pack()
    frame_vege.pack_propagate(False) 
    lbl_vege = Label(frame_vege, text='vegetation: ', fg='light grey')
    lbl_vege.pack(side='left')
    combobox_vege = Combobox(frame_vege, values=list(self.new_dataset.columns), width=15)
    combobox_vege.set('-')  # Texte par défaut
    combobox_vege.pack(side='right')
    combobox_vege.config(state="disabled", foreground='light grey')
    
    # Add ok button
    ok_button = ttk.Button(mode_window, text='OK', command=partial(ok_button_pressed, return_value))
    ok_button.pack(pady=20)
    ok_button.config(state='disabled')

    # bindings
    combobox_mode.bind("<<ComboboxSelected>>", mode_chosen)
    combobox_class.bind("<<ComboboxSelected>>", class_chosen)
    combobox_bare.bind("<<ComboboxSelected>>", mapping_classes)
    combobox_vege.bind("<<ComboboxSelected>>", mapping_classes)

    mode_window.wait_window()
    return return_value[0]


def load(self, mode=0):
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
                        self.sample_index = dict_save['sample_index']
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
                self.sample_index = dict_save['sample_index']
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
            #self.show_image()
            #self.update_infos()

    if self.polygon_path != "" and self.raster_path != "":
        #self.sample_index = 0
        self.show_image()
        # activate categorie buttons
        for idx, (val, label) in enumerate(self.interest_col_val_to_lbl.items()):
            self.lst_buttons_category[idx].config(text=label, state='normal')
            self.attribute_button_command(self.lst_buttons_category[idx], val)
    if self.polygon_path != "" or self.raster_path != "":
        self.update_infos()
    

def save(self):
    if self.UnsavedChanges == 0:
        _ = messagebox.showinfo("Information", "No changes has been detected.")
        return

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
            self.new_dataset.loc[self.new_dataset[self.interest_col] != ""].to_file(new_polygon_src)
        else: # if self.mode  = 'correcter
            self.new_dataset.to_file(new_polygon_src)
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
            'sample_index': self.sample_index,
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
        _ = messagebox.showinfo("Information", f"The changes have been saved in folder :\n{new_polygon_path}")
        self.UnsavedChanges = False

        # compute visualization of data analysis
        if self.mode == 'correcter':
            dict_char_to_num = {'b':0,'t':1,'s':2,'e':3,'l':4,'i':5}
            pred_dataset = self.dataset.loc[list(self.new_dataset.index)]
            true = [dict_char_to_num[x] for x in list(self.new_dataset['class'].values)]
            pred = [dict_char_to_num[x] for x in list(pred_dataset['class'].values)]
            show_confusion_matrix(
                y_pred=pred,
                y_true=true,
                target_src=os.path.join(new_polygon_path, 'performances.png'),
                class_labels=self.frac_col_lbl_to_val.values(),
                title="Performances",
                do_save=True,
                do_show=False,
            )


def exit(self):
    if self.UnsavedChanges == True:
        result = messagebox.askyesnocancel("Confirmation", "There is unsaved changes! Do you want to save?")
        if result == True:
            save(self)
        elif result == False:
            pass
        else:
            return
    self.root.quit()


def order(self):
    def ok_button_pressed(window, combobox, radio_selection):
        if combobox.get() == "Select an option":
            window.destroy()
            return
        self.order_var = combobox.get()
        order = radio_selection.get()
        self.order_asc = order == 'asc'

        # update dataframe to show
        self.dataset_to_show = self.dataset_to_show.sort_values(
            by=[self.order_var], 
            axis=0, 
            ascending= self.order_asc)
        self.show_image()
        self.update_infos()
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
        checked_texts = [str(tree.item(item, "text")) for item in checked_items]
        self.shown_cat = checked_texts
        shown_cat_keys = [key for key,val in self.frac_col_val_to_lbl.items() if val in self.shown_cat]
        indexes = self.new_dataset.loc[self.new_dataset[self.frac_col].astype('string').isin(shown_cat_keys)].index
        self.dataset_to_show = self.new_dataset.loc[indexes].copy()
        self.num_dataset_to_show = len(self.dataset_to_show)
        #self.sample_index = 0
        # keep current or go to next
        if self.sample_index not in list(self.dataset_to_show.index):
            self.show_next_image()
        """if self.frac_col_val_to_lbl[self.dataset_to_show.loc[self.sample_index, self.frac_col]].isin(self.cat_to_show):
            self.show_image()
            self.update_infos()
        else:
            self.show_next_image()"""
        self.update_infos()
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
        self.show_image()
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


def remove_sample(self):
    # verify if polygon loaded
    if len(self.new_dataset) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        return
    
    # confirmation
    if not messagebox.askyesno("Confirmation", "You are about to remove this sample. Are you sure?"):
        return


    # remove sample
    self.dataset_to_show = self.dataset_to_show.drop(self.sample_index, axis=0)
    #self.new_dataset = self.new_dataset.drop(self.sample_index, axis=0)
    
    # add in corresponding list for potential retrieval
    self.changes_log.append("removing " + str(self.sample_index))
    self.UnsavedChanges = True
    self.show_next_image()


if __name__ == '__main__':
    """polygon_path = "D:/GitHubProjects/STDL_Classifier/data/sources/gt_MNC_filtered.gpkg"
    data = gpd.read_file(polygon_path)
    data.drop('geometry', axis=1).to_csv("D:/GitHubProjects/STDL_Classifier/data/sources/gt_MNC_filtered_corrected/gt_MNC_filtered.gpkg.csv", sep=';', index=None)"""
    lst = ['a', 'b', 'c']
    lst.remove('a')
    print(lst)