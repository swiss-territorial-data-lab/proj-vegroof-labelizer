import os
import tkinter as tk
from tkinter import Tk, Menu, Label, Button, Frame, font, filedialog, messagebox, Checkbutton, Scrollbar, IntVar, Canvas,Toplevel, Text
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from functools import partial
from src.menu_utils import *
from src.image_utils import show_image, zoom, drag_image, start_drag, update_image


class ImageViewer:
    def __init__(self, root):
        self.UnsavedChanges = False
        self.root = root
        self.polygon_path = ""
        self.raster_path = ""
        self.sample_index = 0
        self.num_dataset_to_show = 0
        self.dataset = gpd.GeoDataFrame()
        self.new_dataset = gpd.GeoDataFrame()
        self.dataset_to_show = gpd.GeoDataFrame()
        self.list_rasters_src = []
        self.changes_log = []
        #self.id_sec = 0
        self.shown_cat = []
        self.shown_meta = []
        self.infos_files = {
            'Polygons loc': '-',
            'Rasters loc': '-',
            'sample shown': '0/0',
        }

        #   _ordering variables
        self.order_var = None
        self.order_asc = True

        self.label_to_class = {}
        self.class_to_label = {}
        self.frac_col = ""
        self.interest_col = ""
        self.frac_col_lbl_to_val = {}
        self.frac_col_val_to_lbl = {}
        self.interest_col_lbl_to_val = {}
        self.interest_col_val_to_lbl = {}

        self.metadata = {}

        #   _input variables
        self.input_class_name = ""
        self.mode = ""
        #self.input_bin_class_values = {}

        # Set a custom font style for the app
        self.custom_font = font.Font(family="Helvetica", size=10, weight="bold")

        # Set the main window
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        root.geometry(f"800x800+{int(screen_width/2-400)}+{int(screen_height/2-400)}")
        root.resizable(False,False)
        root.configure(bg="#2c3e50")
        root.title('GeoLabelizer')
        
        # Create the menu
        menu_bar = Menu(root)
        
        #   _add loading menu
        load_menu = Menu(menu_bar, tearoff=0)
        load_menu.add_command(label='Polygons', command=partial(load, self, 1))
        load_menu.add_command(label='Rasters', command=partial(load, self, 2))
        load_menu.add_command(label='Polygons & Rasters', command=partial(load, self, 0))
        load_menu.add_command(label='From save', command=partial(load, self, 3))
        menu_bar.add_cascade(label='Load', menu=load_menu)

        #   _add selection of categories and metadata to show
        select_menu = Menu(menu_bar, tearoff=0)
        select_menu.add_command(label="categories to show", command=partial(open_list_cat, self))
        select_menu.add_command(label="metadata to show", command=partial(open_list_meta, self))
        menu_bar.add_cascade(label='Select', menu=select_menu)

        #   _add ordering
        menu_bar.add_command(label="Order", command=partial(order, self))

        #   _add save and exit options
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
        self.current_zoom = 1.0  # Initial zoom level
        self.initial_zoom = 0.0
        self.offset_x = 0
        self.offset_y = 0

        # Get the image dimensions
        img_dim = 512
        self.img_width, self.img_height = (img_dim, img_dim)

        #self.image = Label(root)
        self.image = Canvas(root, width=self.img_width, height=self.img_height)
        self.image_id = 0
        self.original_image = None
        self.display_image = None
        self.margin_around_image = 50
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

        # set the sample index selector and tot dataset
        label_sample_index_1 = Label(root, text="Go to sample : ", font=file_info_label_font, fg="#ecf0f1", bg="#2c3e50", anchor="center", justify="left")
        label_sample_index_1.place(x=610, y=690)
        self.sample_index_combobox = ttk.Combobox(root, values='-')
        self.sample_index_combobox.set("0")  # Texte par défaut
        self.sample_index_combobox.place(x=720,y=690, width=60)
        self.sample_index_combobox.bind("<<ComboboxSelected>>", self.select_sample)

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

        # Key binding
        #   _samples navigation
        root.bind('a', lambda event: self.show_previous_image())
        root.bind('d', lambda event: self.show_next_image())
        root.bind('<Left>', lambda event: self.show_previous_image())
        root.bind('<Right>', lambda event: self.show_next_image())
        root.bind('<space>', lambda event: self.show_next_image())
        root.bind('<Control-s>', lambda event: save(self))

        #   _image navigation (drag & zoom)
        self.image.bind("<MouseWheel>",lambda event:  zoom(self, event))
        #self.image.bind("<B1-Motion>",lambda event:  drag_image(self, event))
        #self.image.bind("<Button-1>",lambda event:  start_drag(self, event))



        # temp-------------------
        """self.polygon_path = "D:/GitHubProjects/STDL_sample_labelizer/data/sources/inf_binary_LR_RF.gpkg"
        self.raster_path = "D:/GitHubProjects/STDL_sample_labelizer/data/sources/inference"
        self.dataset = gpd.read_file(self.polygon_path)
        self.new_dataset = gpd.read_file(self.polygon_path)
        self.dataset_to_show = gpd.read_file(self.polygon_path)
        for r, d, f in os.walk(self.raster_path):
                for file in f:
                    if file.endswith('.tif'):
                        file_src = r + '/' + file
                        file_src = file_src.replace('\\','/')
                        self.list_rasters_src.append(file_src)
        self.mode = 'labelizer'
        self.input_class_name='pred'
        self.shown_cat = list(self.new_dataset[self.input_class_name].unique())
        self.update_infos()"""
        # -----------------------

        show_image(self)
   
    def show_image(self):
        show_image(self)
    
    def update_image(self):
        update_image(self)

    def show_next_image(self):
        self.sample_index = (self.sample_index + 1) % len(self.dataset_to_show)  # Loop around
        while self.label_to_class[self.dataset_to_show.iloc[self.sample_index][self.input_class_name]] not in self.shown_cat:
            self.sample_index = (self.sample_index + 1) % len(self.dataset_to_show)  # Loop around
        show_image(self)
        self.update_infos()

    def show_previous_image(self):
        self.sample_index = (self.sample_index - 1) % len(self.dataset_to_show)  # Loop around
        while self.label_to_class[self.dataset_to_show.iloc[self.sample_index][self.input_class_name]] not in self.shown_cat:
            self.sample_index = (self.sample_index - 1) % len(self.dataset_to_show)  # Loop around
        show_image(self)
        self.update_infos()
    
    def update_infos(self):
        # update files info
        self.num_dataset_to_show = len(self.dataset_to_show)
        self.infos_files['sample shown'] = f'{self.sample_index + 1} / {self.num_dataset_to_show}'
        self.infos_files['Polygons loc'] = self.polygon_path.split('/')[-1] if self.polygon_path != None else '-'
        self.infos_files['Rasters loc'] = self.raster_path.split('/')[-1] if self.raster_path != None else '-'
        new_text = '\n'.join([key + ': ' + str(val) for key, val in self.infos_files.items()])
        self.label_infos_files.config(text=new_text)

        # security
        if self.raster_path == "" or self.polygon_path == "" or len(self.dataset_to_show) == 0:
            return

        # update metadata
        self.metadata = {}
        for meta in self.shown_meta:
            self.metadata[meta] = self.dataset_to_show.loc[self.sample_index,meta].values[0]
        meta_text = '\n'.join([item[0] + ': ' + str(item[1]) for item in self.metadata.items()])
        self.infos_sample.config(text = meta_text if len(self.metadata) > 0 else '-')

        # update sample selector
        self.sample_index_combobox.config(values=[str(x + 1) for x in range(self.num_dataset_to_show)])
        self.sample_index_combobox.set(str(self.sample_index + 1))

        # update class buttons enabling-state
        map_class_to_button={
            'b': self.bare_button,
            't': self.terrace_button,
            's': self.spontaneous_button,
            'e': self.extensive_button,
            'l': self.lawn_button,
            'i': self.intensive_button,
        }
        cat = ""
        if self.mode == 'correcter':
            cat = self.dataset_to_show.iloc[self.sample_index][self.input_class_name]
        elif self.mode == 'labelizer':
            cat = self.dataset_to_show.iloc[self.sample_index]['class']
        for key, button in map_class_to_button.items():
            if key == cat:
                button.config(state='disabled')
            else:
                button.config(state='enabled')

        if self.sample_index == self.num_dataset_to_show - 1:
            messagebox.showinfo("informaton", "Last sample reached !")

    def change_category(self, cat):
        self.new_dataset.loc[self.sample_index, 'class'] = cat
        self.dataset_to_show.loc[self.sample_index, 'class'] = cat
        self.UnsavedChanges = True
        self.changes_log.append(f"Changing category of sample with index {self.sample_index} to '{cat}'")

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
                self.title.config(text=f"sample {self.sample_index} - {label}")
            else:
                button.config(state='normal')
        self.update_infos()
        #self.root.after(300, self.show_next_image)
        
    def select_sample(self, event):
        self.sample_index = int(self.sample_index_combobox.get()) - 1
        show_image(self)
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
