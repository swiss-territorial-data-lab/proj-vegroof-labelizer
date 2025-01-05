import os
import tkinter as tk
from tkinter import Tk, Menu, Label, Button, Frame, font, filedialog, messagebox, Checkbutton, Scrollbar, IntVar, Canvas,Toplevel, Text
from tkinter import ttk
from PIL import Image, ImageTk
from time import sleep
import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from functools import partial
import threading
from src.menu_utils import *
from src.image_utils import show_image, zoom, drag_image, start_drag, update_image


class ImageViewer:
    def __init__(self, root):
        self.UnsavedChanges = False
        self.root = root
        self.polygon_path = ""
        self.raster_path = ""
        self.sample_index = 0
        self.sample_pos = 0
        self.num_dataset_to_show = 0
        self.dataset = gpd.GeoDataFrame()
        self.new_dataset = gpd.GeoDataFrame()
        self.dataset_to_show = gpd.GeoDataFrame()
        self.old_crs = ""
        self.new_crs = ""
        self.list_rasters_src = []
        self.changes_log = []
        self.shown_cat = []
        self.id_cols = []
        self.shown_meta = []
        self.infos_files = {
            'Polygons loc': '-',
            'Rasters loc': '-',
            'sample shown': '0/0',
        }

        #   _ordering variables and metadata
        self.order_var = ""
        self.order_asc = True
        self.metadata = {}

        self.zooming_max = 1.5
        self.drag_prop_to_zoom = True
        self.margin_around_image = 50
      

        #   _input variables
        self.frac_col = ""
        self.interest_col = ""
        self.frac_col_lbl_to_val = {}
        self.frac_col_val_to_lbl = {}
        self.interest_col_lbl_to_val = {}
        self.interest_col_val_to_lbl = {}
        self.mode = ""

        #   _buffer
        self.buffer = None
        self.buffer_front_max_size = 10
        self.buffer_back_max_size = 5

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

        #   _add settings
        menu_bar.add_command(label='Settings', command=partial(open_settings, self))

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
        self.loading_lbl = Label(root, text="",
                                  font=img_info_font, 
                                  fg="#ecf0f1", 
                                  bg="#2c3e50",
                                  anchor="center",
                                  justify="left",
        )
        self.loading_lbl.place(x=550, y=685)

        # Prepare loading images
        self.loading_frames = [tk.PhotoImage(file="src/loading.gif", format=f"gif -index {i}") for i in range(12)]
        self.current_loading_frame = 0
        self.loading_running = False

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
        self.prev_button = ttk.Button(self.nav_button_frame, text="Previous", state='disabled', command=self.show_previous_image)
        self.prev_button.pack(side="left", padx=20)
        self.next_button = ttk.Button(self.nav_button_frame, text="Next", state='disabled', command=self.show_next_image)
        self.next_button.pack(side="right", padx=20)

        # Create category buttons
        self.lst_buttons_category = []
        for i in range(6):
            new_button = ttk.Button(self.class_button_frame, text="-", state='disabled')
            new_button.pack(side="left", padx=5)
            self.lst_buttons_category.append(new_button)

        # Create buffer labels
        self.buffer_front_lbl_state = Label(root, text=f"Front Buffer : 0/{self.buffer_front_max_size}",
                                  font=file_info_label_font, 
                                  fg="#ecf0f1", 
                                  bg="#2c3e50",
                                  anchor="center",
                                  justify="left",
        )
        self.buffer_front_lbl_state.place(x=20, y=640)
        self.buffer_back_lbl_state = Label(root, text=f"Back Buffer : 0/{self.buffer_back_max_size}",
                                  font=file_info_label_font, 
                                  fg="#ecf0f1", 
                                  bg="#2c3e50",
                                  anchor="center",
                                  justify="left",
        )
        self.buffer_back_lbl_state.place(x=20, y=660)
        self.buffer_infos_lbl = Label(root, text="",
                                  font=file_info_label_font, 
                                  fg="red", 
                                  bg="#2c3e50",
                                  anchor="center",
                                  justify="left",
        )
        self.buffer_infos_lbl.place(x=400, y=640)

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
        self.image.bind("<B1-Motion>",lambda event:  drag_image(self, event))
        self.image.bind("<Button-1>",lambda event:  start_drag(self, event))

        show_image(self)
        threading.Thread(target=self.auto_process).start()
        # self.running = True
        # self.animate_loading_icon()

    def auto_process(self):
        # infos about buffers
        if self.buffer:
            self.buffer_front_lbl_state.config(text=f"Front Buffer : {min(self.buffer.buffer_front_size.value, self.buffer_front_max_size)}/{self.buffer_front_max_size}")
            self.buffer_back_lbl_state.config(text=f"Back Buffer : {min(self.buffer.buffer_back_size.value, self.buffer_back_max_size)}/{self.buffer_back_max_size}")

        if self.loading_running == True:
            self.animate_loading_icon()
        else:
            self.loading_lbl.config(image='')
        self.root.after(100, self.auto_process)

    def start_process(self):
            self.running = True
            self.start_button.config(state=tk.DISABLED)

            # Start the animation
            self.animate_loading_icon()

            # Run the time-consuming task in a separate thread
            threading.Thread(target=self.long_task, daemon=True).start()


    def animate_loading_icon(self):
        if self.loading_running:
            # Update the icon
            self.loading_lbl.config(image=self.loading_frames[self.current_loading_frame])
            self.current_loading_frame = (self.current_loading_frame + 1) % len(self.loading_frames)
            # Schedule the next frame
            self.root.after(100, self.animate_loading_icon)

    def show_image(self):
        show_image(self)
    
    def update_image(self):
        update_image(self)
    
    def show_next_image(self):
        def thread_target():
            try:
                while self.buffer.buffer_front_size.value == 1 or self.buffer.buffer_back_size.value == 1:
                    sleep(0.5)
                    self.loading_running = True
                self.loading_running = False
                self.buffer.move_forward()
            except Exception as e:
                print(f"Error in thread: {e}")
            finally:
                # Update current shown sample
                self.sample_pos = self.buffer.current_pos
                self.sample_index = self.dataset_to_show.index[self.sample_pos]
                show_image(self)
                self.update_infos()

        if self.num_dataset_to_show == 0:
            show_image(self)
            return
        
        # Handle navigation buttons
        self.prev_button.config(state='disabled')
        self.next_button.config(state='disabled')

        # Start the thread
        thread = threading.Thread(target=thread_target)
        thread.start()

    def show_previous_image(self):
        def thread_target():
            try:
                while self.buffer.buffer_front_size.value == 1 or self.buffer.buffer_back_size.value == 1:
                    sleep(0.5)
                    self.loading_running = True
                self.loading_running = False
                self.buffer.move_backward()
            except Exception as e:
                print(f"Error in thread: {e}")
            finally:
                # Update current shown sample
                self.sample_pos = self.buffer.current_pos
                self.sample_index = self.dataset_to_show.index[self.sample_pos]
                show_image(self)
                self.update_infos()

        if self.num_dataset_to_show == 0:
            show_image(self)
            return
        
        # Handle navigation buttons
        self.prev_button.config(state='disabled')
        self.next_button.config(state='disabled')

        # Start the thread
        thread = threading.Thread(target=thread_target)
        thread.start()
    
    def update_infos(self):
        # update files info
        self.num_dataset_to_show = len(self.dataset_to_show)
        self.sample_pos = 0
        if self.num_dataset_to_show > 0:
            self.sample_pos = self.dataset_to_show.index.get_loc(self.sample_index)
        self.infos_files['sample shown'] = f'{min([self.sample_pos + 1, self.num_dataset_to_show])} / {self.num_dataset_to_show}'
        self.infos_files['Polygons loc'] = self.polygon_path.split('/')[-1] if self.polygon_path != None else '-'
        self.infos_files['Rasters loc'] = self.raster_path.split('/')[-1] if self.raster_path != None else '-'
        new_text = '\n'.join([key + ': ' + str(val) for key, val in self.infos_files.items()])
        self.label_infos_files.config(text=new_text)

        # # update navigation buttons
        if self.num_dataset_to_show == 0:
            self.next_button.config(state='disabled')
            self.prev_button.config(state='disabled')
            self.removeSample_button.config(state='disabled')
        else:
            self.next_button.config(state='normal')
            self.prev_button.config(state='normal')
            self.removeSample_button.config(state='normal')

        # security
        if self.raster_path == "" or self.polygon_path == "" or len(self.dataset_to_show) == 0:
            return

        # update metadata
        self.metadata = {}
        for meta in self.shown_meta:
            self.metadata[meta] = str(self.dataset_to_show.loc[self.sample_index,meta])
        meta_text = '\n'.join([item[0] + ': ' + str(item[1]) for item in self.metadata.items()])
        self.infos_sample.config(text = meta_text if len(self.metadata) > 0 else '-')

        # update image title
        cat_selection = self.dataset_to_show.loc[self.sample_index, self.frac_col]
        cat_interest = self.dataset_to_show.loc[self.sample_index, self.interest_col]
        interest_lbl = self.interest_col_val_to_lbl[cat_interest] if cat_interest != "" else '-'
        if self.mode == 'labelizer':
            select_lbl = self.frac_col_val_to_lbl[str(cat_selection)]
            select_lbl = select_lbl[0:13] + '..' if len(select_lbl) > 15 else select_lbl
            interest_lbl = interest_lbl[0:13] + '..' if len(interest_lbl) > 15 else interest_lbl
            #interest_lbl = str(interest_lbl)[0:min(len(str(interest_lbl)), 10)]
            self.title.config(text=f"select val: {select_lbl} | new val: {interest_lbl}")
        elif self.mode == 'correcter':
            self.title.config(text=f"value: {interest_lbl}")
        else:
            self.title.config(text="No sample to display")

        # update sample selector
        self.sample_index_combobox.config(values=[str(x + 1) for x in range(self.num_dataset_to_show)])
        self.sample_index_combobox.set(str(self.dataset_to_show.index.get_loc(self.sample_index) + 1))

        # update class buttons enabling-state
        for button in self.lst_buttons_category:
            text = button.cget('text')
            if cat_interest == "":
                button.config(state='normal' if text != '-' else 'disabled')
            elif text == self.interest_col_val_to_lbl[cat_interest]:
                button.config(state='disabled')
            elif text in self.interest_col_val_to_lbl.values():
                button.config(state='normal')
        if self.sample_pos == self.num_dataset_to_show - 1:
            messagebox.showinfo("informaton", "Last sample reached !")

        # loop every 100ms
        # self.root.after(100, self.update_infos)

    def attribute_button_command(self, button: ttk.Button, val):
        def change_category(self, cat):
            self.new_dataset.loc[self.sample_index, self.interest_col] = cat
            self.dataset_to_show.loc[self.sample_index, self.interest_col] = cat
            if self.mode == 'correcter':
                self.new_dataset.loc[self.sample_index, self.frac_col] = cat
                self.dataset_to_show.loc[self.sample_index, self.frac_col] = cat
                """if self.frac_col_val_to_lbl[str(cat)] not in self.shown_cat:
                    self.dataset_to_show = self.dataset_to_show.drop(self.sample_index)
                    self.sample_index = self.dataset_to_show.index[self.sample_pos]
                    self.show_image()"""

            self.UnsavedChanges = True
            self.changes_log.append(f"Changing category of sample with index {self.sample_index} to '{cat}'")
            self.update_infos()
        button.config(command=partial(change_category, self, val))

    def select_sample(self, event):
        # Update position
        self.sample_pos = int(self.sample_index_combobox.get()) - 1
        self.sample_index = self.dataset_to_show.index[self.sample_pos]

        # Prepare for buffer reset
        self.buffer.current_pos = self.sample_pos
        self.buffer.current_file_path = ""
        self.original_image = None
        self.display_image = None


        # # Synchronization event to signal when the thread is done
        # thread_done = threading.Event()

        # # 
        # def thread_target():
        #     try:
        #         self.buffer.reset()
        #     except Exception as e:
        #         print(f"Error in thread: {e}")
        #     finally:
        #         thread_done.set()  # Signal that the thread is done

        # # Start the thread
        # thread = threading.Thread(target=thread_target)
        # thread.start()

        # # Wait for the thread to finish (in order to avoid read-write conflicts)
        # while not thread_done.is_set():
        #     sleep(0.1)

        try:
            self.buffer.reset()
        except Exception as e:
            print("an error occured while reseting buffer: ", e)
        finally:
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
