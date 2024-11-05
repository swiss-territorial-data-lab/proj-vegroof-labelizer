import tkinter as tk
import os
from tkinter import Tk, Menu, Label, Button, Frame, font, filedialog, messagebox, Checkbutton, Scrollbar, IntVar, Canvas,Toplevel
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
from ttkwidgets import CheckboxTreeview
import geopandas as gpd
from functools import partial

def load(self, mode=0):
    # load polygon
    if mode in [0,1]:
        self.polygon_path = filedialog.askopenfilename(
        title="Select the vector source",
        filetypes=[("GeoPackage Files", "*.gpkg"), ("All Files", "*.*")]
        )
        if self.polygon_path:
            print(f"Selected file: {self.polygon_path}")
            self.roofs = gpd.read_file(self.polygon_path)
            self.new_roofs = gpd.read_file(self.polygon_path)
            self.roofs_to_show = gpd.read_file(self.polygon_path)
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

        self.new_roofs.to_file(new_polygon_src)
        self.new_roofs.drop('geometry', axis=1).to_csv(new_polygon_src+".csv", sep=';', index=None)

        # create list of removed samples
        with open(os.path.join(new_polygon_path, 'list_removed_samples.txt'), 'w') as file:
            for egid in self.changes_log:
                file.write(f"{egid}\n")
            #file = self.list_removed_samples
    except AttributeError:
        _ = messagebox.showerror("Error", "A problem happened! Either the path to the polygon has not been set or is non-existant.")
    else:
        _ = messagebox.showinfo("Information", f"The changes have been saved in folder :\n{new_polygon_path}")
        self.UnsavedChanges = False

        # compute visualization of data analysis
        

    return


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
    quit()


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
    order_window.geometry("300x200")

    # add label
    label = Label(order_window, text="Select ordering item:")
    label.pack()

    # Créer la Combobox
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
    checkbox_window.geometry("300x300")

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
    checkbox_window.geometry("300x300")

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