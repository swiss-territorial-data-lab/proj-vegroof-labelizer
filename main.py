import os
import tkinter as tk
from tkinter import Tk, Menu, Label, Button, Frame, font, filedialog, messagebox, Checkbutton, Scrollbar, IntVar, Canvas,Toplevel, Text
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import fiona # for .exe creation
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from functools import partial
from src.menu_utils import *
from time import sleep

# Global variables (to set before running the software)
# ==============================
"""INPUT_CLASS_NAME = "class"  # name of the column that contain the category in the gpkg file to process
MODE = 'correcter'  # to choose in ['labelizer', 'correcter']
INPUT_BIN_CLASS_VALUES = {  # if the gpkg file to process is one, with binary classes, the values used for each class
    "bare": 0,
    "vegetated": 1,
}"""

# ==============================

class ImageViewer:
    def __init__(self, root):
        self.UnsavedChanges = False
        self.root = root
        self.polygon_path = None
        self.raster_path = None
        self.roof_index = 0
        self.num_roofs_to_show = 0
        self.roofs = gpd.GeoDataFrame()
        self.new_roofs = gpd.GeoDataFrame()
        self.roofs_to_show = gpd.GeoDataFrame()
        self.list_rasters_src = []
        self.changes_log = []
        self.egid = 0
        self.shown_cat = []
        self.shown_meta = []
        self.infos_files = {
            'Polygons loc': '-',
            'Rasters loc': '-',
            'Roof shown': '0/0',
        }

        # _ ordering variables
        self.order_var = None
        self.order_asc = True

        self.label_to_class_name = {
            'b': ['bare', 0],
            't': ['terrace', 1],
            's': ['spontaneous', 2],
            'e': ['extensive', 3],
            'l': ['lawn', 4],
            'i': ['intensive', 5],
        }

        self.metadata = {}

        # _ input variables
        """self.input_class_name = INPUT_CLASS_NAME
        self.mode = MODE
        self.input_bin_class_values = INPUT_BIN_CLASS_VALUES"""
        self.input_class_name = ""
        self.mode = ""
        self.input_bin_class_values = {}

        # Set a custom font style for the app
        self.custom_font = font.Font(family="Helvetica", size=10, weight="bold")

        # Set the main window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"800x800+{int(screen_width/2-400)}+{int(screen_height/2-400)}")
        root.resizable(False,False)
        root.configure(bg="#2c3e50")
        
        # Create the menu
        menu_bar = Menu(root)
        
        # _ add loading menu
        load_menu = Menu(menu_bar, tearoff=0)
        load_menu.add_command(label='Polygons', command=partial(load, self, 1))
        load_menu.add_command(label='Rasters', command=partial(load, self, 2))
        load_menu.add_command(label='Polygons & Rasters', command=partial(load, self, 0))
        menu_bar.add_cascade(label='Load', menu=load_menu)

        # _ add selection of categories and metadata to show
        select_menu = Menu(menu_bar, tearoff=0)
        select_menu.add_command(label="categories to show", command=partial(open_list_cat, self))
        select_menu.add_command(label="metadata to show", command=partial(open_list_meta, self))
        menu_bar.add_cascade(label='Select', menu=select_menu)

        # _ add ordering
        menu_bar.add_command(label="Order", command=partial(order, self))

        # _ add save and exit options
        menu_bar.add_command(label='Save', command=partial(save, self))
        menu_bar.add_command(label='Exit', command=partial(exit, self))

        # _ attach the menu bar to the root window
        root.config(menu=menu_bar)

        # Set the infos about loaded rasters and polygons
        text_infos = '\n'.join([item[0] + ': ' + str(item[1]) for item in self.infos_files.items()])
        file_info_label_font = font.Font(family="Helvetica", size=10, weight="bold", slant="italic")
        self.label_infos_files =  Label(root, text=text_infos, font=file_info_label_font, fg="#ecf0f1", bg="#2c3e50", anchor="center", justify="left")
        self.label_infos_files.place(x=10, y=10)

        # style of buttons
        style = ttk.Style()
        style.theme_use("clam")  # Try 'clam', 'default', 'alt', etc.
        style.configure("TButton", font=self.custom_font, foreground="#ecf0f1", background="#3498db", padding=6)
        style.configure("")
        style.map("TButton", background=[("active", "#2980b9")])
        
        # Define a custom style for the special button
        style.configure("Special.TButton", background="red")
        style.map('Special.TButton',  background=[("active", "#c90000")])

        # Add remove-sample button
        self.removeSample_button = ttk.Button(root, text="Remove sample", style='Special.TButton', command=partial(remove_sample, self))
        self.removeSample_button.place(x=620, y=30, width=150)

        # Set the title
        title_label_font = font.Font(family="Helvetica", size=16, weight="bold", slant="italic")
        self.title = Label(root, text="",
                           font=title_label_font,         # Set custom font
                           fg="#ecf0f1",             # Set text color
                           bg="#2c3e50",             # Match background color to root
                           anchor="center",          # Center align text
                           justify="center",         # Center align multi-line text
        )
        self.title.place(x=20,y=80, width=520)
        
        # Display image and image info
        self.image = Label(root)
        self.image.place(x=20, y=120)
        img_info_font = font.Font(family="Helvetica", size=12, weight="bold", slant="italic")
        self.infos_sample = Label(root, text="",
                                  font=img_info_font, 
                                  fg="#ecf0f1", 
                                  bg="#2c3e50",
                                  anchor="center",
                                  justify="left",
        )
        self.infos_sample.place(x=540, y=120)

        # set the roof index selector and tot roofs
        label_roof_index_1 = Label(root, text="Go to sample : ", font=file_info_label_font, fg="#ecf0f1", bg="#2c3e50", anchor="center", justify="left")
        label_roof_index_1.place(x=610, y=690)
        self.roof_index_combobox = ttk.Combobox(root, values='-')
        self.roof_index_combobox.set("0")  # Texte par défaut
        self.roof_index_combobox.place(x=720,y=690, width=60)
        self.roof_index_combobox.bind("<<ComboboxSelected>>", self.select_sample)

        # Set the frames of class buttons
        self.class_button_frame = Frame(root)
        self.class_button_frame.pack(side="bottom", pady=20)  # Add position and padding to frame
        self.class_button_frame.configure(bg="#2c3e50")

        
        # Set the frames of navigation buttons
        self.nav_button_frame = Frame(root)
        self.nav_button_frame.pack(side="bottom", pady=10) # Add position and padding to frame
        self.nav_button_frame.configure(bg="#2c3e50")

        # Create navigation buttons
        self.prev_button = ttk.Button(self.nav_button_frame, text="Previous", command=self.show_previous_image)
        self.prev_button.pack(side="left", padx=20)
        self.next_button = ttk.Button(self.nav_button_frame, text="Next", command=self.show_next_image)
        self.next_button.pack(side="right", padx=20)

        # Create class buttons
        self.bare_button = ttk.Button(self.class_button_frame, text="Bare", command=partial(self.change_category, "b"))
        self.bare_button.pack(side="left", padx=5)
        self.terrace_button = ttk.Button(self.class_button_frame, text="Terrace", command=partial(self.change_category, "t"))
        self.terrace_button.pack(side="left", padx=5)
        self.spontaneous_button = ttk.Button(self.class_button_frame, text="Spontaneous", command=partial(self.change_category, "s"))
        self.spontaneous_button.pack(side="left", padx=5)
        self.extensive_button = ttk.Button(self.class_button_frame, text="Extensive", command=partial(self.change_category, "e"))
        self.extensive_button.pack(side="left", padx=5)
        self.lawn_button = ttk.Button(self.class_button_frame, text="Lawn", command=partial(self.change_category, "l"))
        self.lawn_button.pack(side="left", padx=5)
        self.intensive_button = ttk.Button(self.class_button_frame, text="Intensive", command=partial(self.change_category, "i"))
        self.intensive_button.pack(side="left", padx=5)

        # key mapping
        root.bind('a', lambda event: self.show_previous_image())
        root.bind('d', lambda event: self.show_next_image())
        root.bind('<Left>', lambda event: self.show_previous_image())
        root.bind('<Right>', lambda event: self.show_next_image())
        root.bind('<space>', lambda event: self.show_next_image())
        root.bind('<Control-s>', lambda event: save(self))

        # temp-------------------
        self.polygon_path = "D:/GitHubProjects/STDL_Classifier/data/sources/gt_MNC_filtered.gpkg"
        self.raster_path = "D:/GitHubProjects/STDL_Classifier/data/sources/scratch_dataset"
        self.roofs = gpd.read_file("D:/GitHubProjects/STDL_Classifier/data/sources/gt_MNC_filtered.gpkg")
        self.new_roofs = gpd.read_file("D:/GitHubProjects/STDL_Classifier/data/sources/gt_MNC_filtered.gpkg")
        self.roofs_to_show = gpd.read_file("D:/GitHubProjects/STDL_Classifier/data/sources/gt_MNC_filtered.gpkg")
        for r, d, f in os.walk("D:/GitHubProjects/STDL_Classifier/data/sources/scratch_dataset"):
                for file in f:
                    if file.endswith('.tif'):
                        file_src = r + '/' + file
                        file_src = file_src.replace('\\','/')
                        self.list_rasters_src.append(file_src)
        self.mode = 'correcter'
        self.input_class_name='class'
        self.shown_cat = list(self.new_roofs[self.input_class_name].unique())
        self.update_infos()
        # -----------------------

        self.show_image()
   
    def show_image(self):
        if len(self.list_rasters_src) == 0 or len(self.roofs_to_show) == 0:
            image = Image.open("./no_image.png").resize((512, 512), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            self.image.config(image=self.photo)
            self.title.config(text="No sample to display")
            return

        # get image from polygon and rasters
        while self.roofs_to_show.iloc[self.roof_index][self.input_class_name] not in self.shown_cat:
            self.roof_index += 1
        roof = self.roofs_to_show.iloc[self.roof_index]
        self.egid = roof.EGID
        cat = roof[self.input_class_name]
        geom = roof.geometry

        matching_rasters = []
        matching_images = []
        for raster_src in self.list_rasters_src:
            raster = rasterio.open(raster_src)
            try:
                img_arr, _ = mask(raster, [geom], crop=True)
            except ValueError:
                continue
            else:
                matching_rasters.append(raster)
                matching_images.append(img_arr)

        # test if polygon match with one or multiple rasters:    
        if len(matching_rasters) == 0:
            image = Image.open("./src/no_image.png").resize((512, 512), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(image)
            self.image.config(image=self.photo)
        elif len(matching_rasters) == 1:
            img_arr = matching_images[0]
        else:
            img_size_max = np.sum(matching_images[0].shape)
            img_arr = matching_images[0]
            for img in matching_images:
                if np.sum(img.shape) > img_size_max:
                    img_size_max = np.sum(img.shape)
                    img_arr = img

        # transform if image is in 16bits:
        if img_arr.dtype == 'uint16':
            img_arr = (img_arr/np.max(img_arr) * 255).astype('uint8')

        # show results
        img_arr = np.moveaxis(img_arr[1:4,...], 0, 2)
        image = Image.fromarray(img_arr)

        # _resize image
        max_size = np.max(img_arr.shape[:2])
        ratio = 512 / max_size
        new_size = np.flip((np.array(img_arr.shape[0:2]) * ratio).astype(int))
        image_resized = np.array(image.resize(new_size, Image.Resampling.LANCZOS))  # Resize for display

        # _add padding
        min_axis = np.argmin(image_resized.shape[:2])
        min_size = np.min(image_resized.shape[:2])
        padding_size = int((512 - min_size)/2)
        padding = [(padding_size, padding_size), (0, 0), (0, 0)] if min_axis == 0 else [(0, 0), (padding_size, padding_size), (0, 0)]
        padded_image = np.pad(image_resized,padding, mode='constant')
        
        # control sizes
        for ax in range(2):
            while padded_image.shape[ax] < 512:
                additional_padding = np.zeros((1,padded_image.shape[1],3)) if ax == 0 else np.zeros((padded_image.shape[0], 1,3))
                padded_image = np.concatenate((padded_image, additional_padding), axis=ax)

        # _show image and title
        image_final = Image.fromarray(np.uint8(padded_image))
        self.photo = ImageTk.PhotoImage(image_final)
        if self.mode == 'correcter':
            self.title.config(text=str(int(self.egid)) + ' - ' + self.label_to_class_name[cat][0])
        else:
            self.title.config(text=str(int(self.egid)) + ' - ' + cat)
        self.image.config(image=self.photo)

    def show_next_image(self):
        self.roof_index = (self.roof_index + 1) % len(self.roofs_to_show)  # Loop around
        while self.roofs_to_show.iloc[self.roof_index][self.input_class_name] not in self.shown_cat:
            self.roof_index = (self.roof_index + 1) % len(self.roofs_to_show)  # Loop around
        self.show_image()
        self.update_infos()

    def show_previous_image(self):
        self.roof_index = (self.roof_index - 1) % len(self.roofs_to_show)  # Loop around
        while self.roofs_to_show.iloc[self.roof_index][self.input_class_name] not in self.shown_cat:
            self.roof_index = (self.roof_index - 1) % len(self.roofs_to_show)  # Loop around
        self.show_image()
        self.update_infos()
    
    
    def update_infos(self):
        # update files info
        self.num_roofs_to_show = len(self.roofs_to_show.loc[self.roofs_to_show[self.input_class_name].isin(self.shown_cat)])
        self.infos_files['Roof shown'] = f'{self.roof_index + 1} / {self.num_roofs_to_show}'
        self.infos_files['Polygons loc'] = self.polygon_path.split('/')[-1] if self.polygon_path != None else '-'
        self.infos_files['Rasters loc'] = self.raster_path.split('/')[-1] if self.raster_path != None else '-'
        new_text = '\n'.join([item[0] + ': ' + str(item[1]) for item in self.infos_files.items()])
        self.label_infos_files.config(text=new_text)

        # update metadata
        self.metadata = {}
        for meta in self.shown_meta:
            self.metadata[meta] = self.roofs_to_show.loc[self.roofs_to_show.EGID == self.egid,meta].values[0]
        meta_text = '\n'.join([item[0] + ': ' + str(item[1]) for item in self.metadata.items()])
        self.infos_sample.config(text = meta_text if len(self.metadata) > 0 else '-')

        # update sample selector
        self.roof_index_combobox.config(values=[str(x + 1) for x in range(self.num_roofs_to_show)])
        self.roof_index_combobox.set(str(self.roof_index + 1))

        # update class buttons enabling-state
        map_class_to_button={
            'b': self.bare_button,
            't': self.terrace_button,
            's': self.spontaneous_button,
            'e': self.extensive_button,
            'l': self.lawn_button,
            'i': self.intensive_button,
        }
        cat = self.roofs_to_show.iloc[self.roof_index]['class']
        for key, button in map_class_to_button.items():
            if key == cat:
                button.config(state='disabled')
            else:
                button.config(state='enabled')

        if self.roof_index == self.num_roofs_to_show - 1:
            messagebox.showinfo("informaton", "Last sample reached !")

    def change_category(self, cat):
        self.new_roofs.loc[self.new_roofs['EGID'] == self.egid, 'class'] = cat
        self.roofs_to_show.loc[self.roofs_to_show['EGID'] == self.egid, 'class'] = cat
        self.UnsavedChanges = True
        self.changes_log.append(f"Changing category of {self.egid} to '{cat}'")

        # update class buttons enabling-state
        map_class_to_button={
            'b': ['bare', self.bare_button],
            't': ['terrace', self.terrace_button],
            's': ['spontaneous', self.spontaneous_button],
            'e': ['extensive', self.extensive_button],
            'l': ['lawn', self.lawn_button],
            'i': ['intensive', self.intensive_button],
        }
        for key, [label, button] in map_class_to_button.items():
            if key == cat:
                button.config(state='disabled')
                self.title.config(text=str(int(self.egid)) + ' - ' + label)
            else:
                button.config(state='normal')
        self.update_infos()
        self.root.after(300, self.show_next_image)
        

        

    def select_sample(self, event):
        self.roof_index = int(self.roof_index_combobox.get()) - 1
        self.show_image()
        self.update_infos()
        
def main():
    # Create the root window
    root = Tk()
    app = ImageViewer(root)
        
    # Override the window's close protocol
    root.protocol("WM_DELETE_WINDOW", partial(exit, app))

    # Run program
    root.mainloop()


if __name__ == '__main__':
    main()
