import os
import pickle
import rasterio
from tkinter import filedialog, messagebox, Toplevel
import geopandas as gpd
import threading
from src.buffer import Buffer
from src.menus import set_all_states, menu_mode_choice

def load(self, mode=0):
    """
    Handles loading of polygons, rasters, and saved project states into the application. 
    Manages unsaved changes, initializes necessary data structures, and updates the UI state.

    Args:
        self: Reference to the parent class instance containing the application's state.
        mode : int, optional
        Specifies the loading mode:
            - 0: Load both polygons and rasters.
            - 1: Load only polygons.
            - 2: Load only rasters.
            - 3: Load a saved project state from a pickle file.

    Returns: None
    """
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
                raise e
            finally:
                self.update_infos()

                # Activate navigation buttons
                set_all_states(self.root, 'normal', self.menu_bar)
                self.loading_running = False
                self.buffer_infos_lbl.config(text="")

                # Start autosave
                self.do_autosave = True
                self.auto_save()

    # test if ongoing unsaved project
    if self.UnsavedChanges == True:
        result = messagebox.askyesnocancel("Confirmation", "There is unsaved changes! Do you want to save?")
        if result == True:
            save(self)
        elif result == False:   # If answer is 'No'
            pass
        else:   # If answer is 'Cancel'
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
                        self.order_var = dict_save['order_var']
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
                self.order_var = ""
                self.order_asc = True

                # show mode choice window
                top_level = Toplevel(self.root)
                is_mode_well_set =  menu_mode_choice(self, top_level)
                if not is_mode_well_set: # make sure that the polygon is well set
                    return
                
                # continue to process input polygons
                if self.mode == 'labelizer':
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
                self.order_var = dict_save['order_var']
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
        set_all_states(self.root, 'disabled', self.menu_bar)
        self.buffer_infos_lbl.config(text="Initialising Temp storages...")
        self.loading_running = True
        self.thread = threading.Thread(target=start_buffer)
        self.thread.start()

    elif self.polygon_path != "" or self.raster_path != "":
        self.update_infos()
    

def save(self, verbose=True):
    """
    Saves the current project state and data to files.

    Parameters:
        verbose : bool  If True, shows a confirmation dialog after saving.

    Returns:
        None
    """
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
            'order_var': self.order_var,
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


def exit(self):
    """
    Handles application exit. Checks for running processes or unsaved changes before quitting.

    Parameters:
        self: object - The instance of the class calling this function.

    Returns:
        None
    """
    # Check if program processing
    # if self.loading_running:
    #     messagebox.showwarning("Process running", "Please, wait for the running processes to finish before quitting.")
    #     return
    # Check if unsaved changes
    if self.UnsavedChanges == True:
        result = messagebox.askyesnocancel("Confirmation", "There is unsaved changes! Do you want to save?")
        if result == True:
            save(self)
        elif result == False:
            pass
        else:
            return
    try:
        # Close thread
        if self.thread:
            self.thread.join()

        # Purge the buffer before quitting
        if self.buffer:
            self.buffer.purge()

        self.root.quit()
    except Exception as e:
        print(f"An error happened during quitting. The temp folder might still be in place but will be automatically reset during next run.\n Error: {e}\nKilling process..")
        os._exit(0)
