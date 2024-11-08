import tkinter as tk
import os
import numpy as np
import pandas as pd
from tkinter import Tk, Menu, Label, Button, Frame, font, filedialog, messagebox, Checkbutton, Scrollbar, IntVar, Canvas,Toplevel
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
from ttkwidgets import CheckboxTreeview
import geopandas as gpd
from functools import partial
from src.processing import show_confusion_matrix


def menu_mode_choice(self, mode_window):
    def ok_button_pressed(return_value):
        if combobox_mode.get() != 'Select and option' and combobox_class != 'Select an option' and combobox_bare != '-' and combobox_vege != '-':
            self.mode = combobox_mode.get()
            self.input_class_name = combobox_class.get()
            self.input_bin_class_values['bare'] = combobox_bare.get()
            self.input_bin_class_values['vegetated'] = combobox_vege.get()

            if self.mode == 'labelizer':
                self.new_roofs = self.new_roofs.loc[self.new_roofs[self.input_class_name].isin(self.input_bin_class_values.values())]
            return_value[0] = True
            mode_window.destroy()
    
    def mode_chosen(event):
        mode = combobox_mode.get()
        if mode in ['labelizer', 'correcter']:
            combobox_class.config(state="enabled")
            if combobox_class.get() != 'Select an option':
                class_chosen(event)
            if self.mode == 'correcter':
                combobox_bare.config(state='disabled')
                combobox_vege.config(state='disabled')
                combobox_bare.set('-')
                combobox_vege.set('-')
                mapping_classes(event)
        else:
            print('no mode selected!')

    def class_chosen(event):  
        class_name = combobox_class.get()
        class_values = list(self.new_roofs[class_name].unique())
        mode = combobox_mode.get()

        if mode == 'labelizer':
            if len(class_values) > 2:
                messagebox.showwarning("warning", "The number of different values is greater than 2. After choosing the one corresponding to bare and vegetation samples, the samples with other values will be dismissed!")
                mode_window.focus_set()

            # set mapping
            combobox_bare.config(state='enabled', values=class_values)
            combobox_vege.config(state='enabled', values=class_values)
        elif mode == 'correcter':
            if set(class_values) != set(['b', 't', 's', 'i', 'e', 'l']):
                messagebox.showerror("error", "The values of the class don't match the ones for multi class!")
                mode_window.focus_set()
                return
            else:
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

    # Retrieve categories from roofs
    if len(self.new_roofs) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        return

    # Create a Toplevel window (popup)
    mode_window.title("Categories selection")
    root_pos = [self.root.winfo_x(), self.root.winfo_y()]
    root_dim = [self.root.winfo_width(), self.root.winfo_height()]
    mode_window.geometry(f"300x350+{int(root_pos[0]+root_dim[0]/2-150)}+{int(root_pos[1]+root_dim[1]/2-300)}")

    # select mode
    label = Label(mode_window, text="Select mode:")
    label.pack(anchor='w', padx=10)

    combobox_mode = ttk.Combobox(mode_window, values=['labelizer', 'correcter'])
    combobox_mode.set("Select an option")  # Texte par défaut
    combobox_mode.pack(pady=20)

    # select label column
    label = Label(mode_window, text="Select the column with the class name:")
    label.pack(anchor='w', padx=10)

    combobox_class = ttk.Combobox(mode_window, values=list(self.new_roofs.columns))
    combobox_class.set("Select an option")  # Texte par défaut
    combobox_class.pack(pady=20)
    combobox_class.config(state="disabled")

    # map label to class
    label = Label(mode_window, text='Values mapping (only in "labelizer" mode):')
    label.pack(anchor='w', padx=10)

    frame_bare = Frame(mode_window, width=250, height=35)
    frame_bare.pack()
    frame_bare.pack_propagate(False) 
    label = Label(frame_bare, text='bare: ')
    label.pack(side='left')
    combobox_bare = ttk.Combobox(frame_bare, values=range(4), width=15)
    combobox_bare.set('-')  # Texte par défaut
    combobox_bare.pack(side='right')
    combobox_bare.config(state="disabled")

    frame_vege = Frame(mode_window, width=250, height=35)
    frame_vege.pack()
    frame_vege.pack_propagate(False) 
    label = Label(frame_vege, text='vegetation: ')
    label.pack(side='left')
    combobox_vege = ttk.Combobox(frame_vege, values=list(self.new_roofs.columns), width=15)
    combobox_vege.set('-')  # Texte par défaut
    combobox_vege.pack(side='right')
    combobox_vege.config(state="disabled")
    
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
    # load polygon
    if mode in [0,1]:
        self.polygon_path = filedialog.askopenfilename(
        title="Select the vector source",
        filetypes=[("GeoPackage Files", "*.gpkg"), ("All Files", "*.*")]
        )
        if self.polygon_path:
            self.roofs = gpd.read_file(self.polygon_path)
            self.new_roofs = gpd.read_file(self.polygon_path)
            
            # show mode choice window
            top_level = Toplevel(self.root)
            is_mode_well_set =  menu_mode_choice(self, top_level)
            if not is_mode_well_set: # make sure that the polygon is well set
                return
            
            # continue to process input polygons
            if self.mode == 'labelizer':
                self.new_roofs.rename(columns={self.input_class_name:'class_binary'}, inplace=True)
                self.input_class_name = 'class_binary'
                for cat, val in self.input_bin_class_values.items():
                    self.new_roofs.class_binary = self.new_roofs.class_binary.astype('string')
                    self.new_roofs.loc[self.new_roofs.class_binary.astype('string') == str(val), 'class_binary'] = cat

                self.new_roofs['class'] = np.nan
            """else: # if mode = 'correcter'
                self.new_roofs = """
            self.roofs_to_show = self.new_roofs.copy()
            self.shown_cat = list(self.new_roofs[self.input_class_name].unique())

    # load rasters
    if mode in [0,2]:
        self.raster_path = filedialog.askdirectory(title="Select the raster source")
        if self.raster_path:
            print(f"Selected folder: {self.raster_path}")
            for r, d, f in os.walk(self.raster_path):
                for file in f:
                    if file.endswith('.tif'):
                        file_src = r + '/' + file
                        file_src = file_src.replace('\\','/')
                        self.list_rasters_src.append(file_src)

    if self.polygon_path and self.raster_path:
        self.show_image()
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
        print(new_polygon_path)
        if not os.path.exists(new_polygon_path):
            os.mkdir(new_polygon_path)

        # create geopackage file
        new_polygon_name = self.polygon_path.split('.')[:-1]
        new_polygon_name = self.polygon_path.split('/')[-1]
        new_polygon_name += "_corrected.gpkg"
        new_polygon_name = ''.join(new_polygon_name)
        new_polygon_src = os.path.join(new_polygon_path, new_polygon_name)

        # save roofs to geopackage and csv
        if self.mode == 'labelizer':
            self.new_roofs.dropna(subset=['class']).to_file(new_polygon_src)
            self.new_roofs.dropna(subset=['class']).drop('geometry', axis=1).to_csv(new_polygon_src+".csv", sep=';', index=None)
        else: # if self.mode  = 'correcter
            self.new_roofs.to_file(new_polygon_src)
            self.new_roofs.drop('geometry', axis=1).to_csv(new_polygon_src+".csv", sep=';', index=None)


        # save list of changes
        with open(os.path.join(new_polygon_path, 'modification_logs.txt'), 'w') as file:
            for egid in self.changes_log:
                file.write(f"{egid}\n")
    except AttributeError:
        _ = messagebox.showerror("Error", "A problem happened! Either the path to the polygon has not been set or is non-existant.")
    else:
        _ = messagebox.showinfo("Information", f"The changes have been saved in folder :\n{new_polygon_path}")
        self.UnsavedChanges = False

        # compute visualization of data analysis
        if self.mode == 'correcter':
            pred = [self.label_to_class_name[x][1] for x in list(self.new_roofs['class'].values)]
            true = [self.label_to_class_name[x][1] for x in list(self.roofs['class'].values)]
            show_confusion_matrix(
                y_pred=pred,
                y_true=true,
                target_src=os.path.join(new_polygon_path, 'performances.png'),
                class_labels=[x[0] for x in self.label_to_class_name],
                title="Performances",
                do_save=True,
                do_show=True,
            )


def exit(self):
    if self.UnsavedChanges == True:
        result = messagebox.askyesnocancel("Confirmation", "There is unsaved changes! Do you want to save?")
        if result == True:
            save(self)
        elif result == False:
            pass
        else:
            print("User clicked Cancel")
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
        self.roofs_to_show = self.roofs_to_show.sort_values(
            by=[self.order_var], 
            axis=0, 
            ascending= self.order_asc, 
            ignore_index=True)
        self.UnsavedChanges = True
        self.show_image()
        self.update_infos()
        window.destroy()

    # Retrieve categories from roofs
    if len(self.new_roofs) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        return
    
    metadatas = list(self.new_roofs.columns)

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
        checked_texts = [tree.item(item, "text") for item in checked_items]
        self.shown_cat = checked_texts
        self.show_image()
        self.update_infos()
        window.destroy()

    # Retrieve categories from roofs
    if len(self.new_roofs) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        return
    
    categories = list(self.new_roofs[self.input_class_name].unique())

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
    for id_cat, cat in enumerate(categories):
        if cat in self.shown_cat:
            tag =('checked')
        else:
            tag = ('unchecked')
        tree.insert("", "end", text=cat, tags = tag)

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

    # Retrieve categories from roofs
    if len(self.new_roofs) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        return
    
    metadatas = list(self.new_roofs.columns)

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
    for id_meta, meta in enumerate(metadatas):
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
    if len(self.new_roofs) == 0 or self.polygon_path == None:
        messagebox.showwarning("Information", "No polygon file loaded!")
        return
    
    # confirmation
    if not messagebox.askyesno("Confirmation", "You are about to remove this sample. Are you sure?"):
        return
    
    # add in corresponding list for potential retrieval
    self.changes_log.append("removing " + str(self.egid))

    # remove sample
    idx = self.roofs_to_show.loc[self.roofs_to_show.EGID == self.egid].index.values[0]
    self.roofs_to_show = self.roofs_to_show.drop(idx, axis=0).reset_index(drop=True)

    idx = self.new_roofs.loc[self.new_roofs.EGID == self.egid].index.values[0]
    self.new_roofs = self.new_roofs.drop(idx, axis=0).reset_index(drop=True)

    self.roof_index -= 1
    self.show_next_image()
    self.UnsavedChanges = True





if __name__ == '__main__':
    """polygon_path = "D:/GitHubProjects/STDL_Classifier/data/sources/gt_MNC_filtered.gpkg"
    data = gpd.read_file(polygon_path)
    data.drop('geometry', axis=1).to_csv("D:/GitHubProjects/STDL_Classifier/data/sources/gt_MNC_filtered_corrected/gt_MNC_filtered.gpkg.csv", sep=';', index=None)"""
    lst = ['a', 'b', 'c']
    lst.remove('a')
    print(lst)