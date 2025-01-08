import os
import glob
import tempfile
import multiprocessing
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.merge import merge
from PIL import Image
from shapely.geometry import Polygon, MultiPolygon
import geopandas as gpd
import numpy as np
from time import sleep
import tkinter as tk
from tkinter import ttk
import shutil
from collections import deque
from multiprocessing import Manager
import threading
import traceback


def clip_and_store(pause_event, polygons, margin_around_image, list_rasters_src, buffer_tasks, buffer_results, buffer_size, buffer_max_size, img_size, temp_dir, buffer_type):
        """
        Worker process to clip rasters and store them in a temp folder.
        """
        while True:
            try:
                if len(buffer_tasks) > 0:
                    task = buffer_tasks[0]
                    if task == "STOP":
                        break

                    sample_pos = task
                    sample = polygons.iloc[sample_pos]
                    geometry = sample.geometry
                    # Define bounding box
                    exterior_coords = []

                    #   _find coords of (sub-)polygons
                    if geometry.geom_type == "Polygon":
                        exterior_coords.extend(geometry.exterior.coords)
                    elif geometry.geom_type == "MultiPolygon":
                        for polygon in geometry.geoms:
                            exterior_coords.extend(polygon.exterior.coords)
                            
                    #   _find most-south/east/north/west points
                    minx = min([coord[0] for coord in exterior_coords])
                    maxx = max([coord[0] for coord in exterior_coords])
                    miny = min([coord[1] for coord in exterior_coords])
                    maxy = max([coord[1] for coord in exterior_coords])
                    deltax = maxx - minx
                    deltay = maxy - miny

                    new_minx = minx - margin_around_image
                    new_maxx = maxx + margin_around_image
                    new_miny = miny - margin_around_image
                    new_maxy = maxy + margin_around_image

                    #   _correct to have a square bounding box
                    diff = abs(deltax - deltay)
                    if deltax > deltay:
                        new_miny -= diff // 2
                        new_maxy += diff // 2
                    else:
                        new_minx -= diff // 2
                        new_maxx += diff // 2

                    geom_large = Polygon([
                        (new_minx, new_miny),  # South-west
                        (new_maxx, new_miny),  # Bottom-right
                        (new_maxx, new_maxy),  # Top-right
                        (new_minx, new_maxy),  # Top-left
                        (new_minx, new_miny),  # Close the polygon
                        ])
                    matching_rasters = []
                    matching_images = []
                    out_transform = {}
                    for raster_src in list_rasters_src:
                        raster = rasterio.open(raster_src)
                        try:
                            img_arr, out_transform = mask(raster, [geom_large], crop=True)
                        except ValueError:
                            continue
                        else:
                            matching_rasters.append(raster)
                            matching_images.append(img_arr)
                    
                    # Test if polygon match with one or multiple rasters:    
                    if len(matching_rasters) == 0:
                        # raise ValueError("Polygon did not match any raster!")
                        buffer_results.append((sample_pos, "no-sample", 0, 0))
                        buffer_size.value += 1
                        print(f"New sample in buffer {buffer_type}: {sample_pos} - no-sample")
                        del buffer_tasks[0]
                        continue
                    elif len(matching_rasters) == 1:
                        img_arr = matching_images[0]
                    else:
                        img_arr, out_transform = merge(
                        sources=matching_rasters, 
                        nodata=0, 
                        bounds=geom_large.bounds,
                        resampling=rasterio.enums.Resampling.nearest
                        )

                    if img_arr.shape[0] == 4:
                        img_arr = img_arr[1:4, ...]
                    if len(img_arr.shape) != 3:
                        raise ValueError("Too many dimensions in the image!")
                    for pos, dim in enumerate(img_arr.shape):
                        if dim == 3:
                            img_arr = np.moveaxis(img_arr, pos, 0)
                            break
                        elif pos == 2:
                            raise ValueError("Too many bands in the image!")
                    # else:
                    #     print(img_arr.shape)
                    #     img_arr = np.moveaxis(img_arr, 2, 0)

                    # Plot the raster and overlay the original polygon
                    img_width = img_arr.shape[1]
                    img_height = img_arr.shape[2]
                    fig, ax = plt.subplots(figsize=(img_width/100, img_height/100), dpi=100)

                    # ax.set_position([0, 0, 1, 1])  # [left, bottom, width, height]
                    #   _display the clipped raster
                    show(img_arr, transform=out_transform, ax=ax, cmap="viridis")

                    coords_to_show = []
                    if geometry.geom_type == "Polygon":
                        coords_to_show = [geometry.exterior.coords]
                    elif geometry.geom_type == "MultiPolygon":
                        for polygon in geometry.geoms:
                            coords_to_show = [polygon.exterior.coords for polygon in geometry.geoms]
                    for coords in coords_to_show:
                        x, y = zip(*coords)
                        ax.plot(x, y, color="yellow", linewidth=2, label="Original Polygon")

                    # Remove axes and adjust layout to eliminate borders
                    plt.axis('off')
                    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

                    #   _render the figure as a NumPy array
                    canvas = FigureCanvas(fig)
                    canvas.draw()
                    img_arr = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
                    img_arr = img_arr.reshape(canvas.get_width_height()[::-1] + (3,))
                    # img_arr = np.moveaxis(img_arr, 0, 2)
                    plt.close()

                    # transform if image is in 16bits:
                    if img_arr.dtype == 'uint16':
                        img_arr = (img_arr/np.max(img_arr) * 255).astype('uint8')

                    # Show results
                    image = Image.fromarray(img_arr)
                    # image_resized = img_arr
                    #   _resize image
                    max_size = np.max(img_arr.shape[:2])
                    ratio = img_size / max_size
                    new_size = np.flip((np.array(img_arr.shape[0:2]) * ratio).astype(int))
                    # image_resized = np.array(image.resize(new_size))  # Resize for display

                    image_resized = np.array(image)

                    #   _add padding
                    min_axis = np.argmin(image_resized.shape[:2])
                    min_size = np.min(image_resized.shape[:2])
                    max_size = np.max(image_resized.shape[:2])
                    padding_size = int((max_size - min_size)/2)
                    padding = [(padding_size, padding_size), (0, 0), (0, 0)] if min_axis == 0 else [(0, 0), (padding_size, padding_size), (0, 0)]
                    padded_image = np.pad(image_resized,padding, mode='constant', constant_values=255)
                    
                    # Control sizes
                    for ax in range(2):
                        while padded_image.shape[ax] < max_size:
                            additional_padding = np.ones((1,padded_image.shape[1],3)) if ax == 0 else np.ones((padded_image.shape[0], 1,3))
                            padded_image = np.concatenate((padded_image, additional_padding), axis=ax)

                    # Save image in tmp file
                    img = Image.fromarray(np.uint8(padded_image))
                    temp_file_path = os.path.join(temp_dir, f"sample_{sample_pos}.png")
                    img.save(temp_file_path)

                    # Notify main process of the result
                    buffer_results.append((sample_pos, temp_file_path, deltax, deltay))
                    buffer_size.value += 1
                    print(f"New sample in buffer {buffer_type}: {sample_pos} - {temp_file_path}")
                    del buffer_tasks[0]
                else:
                    if buffer_size.value > buffer_max_size:
                        if buffer_results[-1][1] != 'no-sample':
                            os.remove(buffer_results[-1][1])
                        del buffer_results[-1]
                        buffer_size.value -= 1
                    while buffer_size.value == buffer_max_size or pause_event.is_set():
                        sleep(0.1)

            except Exception as e:
                # buffer_results.append((sample_pos, f"ERROR: {str(e)}",0,0))
                print("Error during clipping: ", e)
                for frame in traceback.extract_tb(e.__traceback__):
                    print(f"File: {frame.filename}, Line: {frame.lineno}, Function: {frame.name}")
                buffer_size.value += 1
        print('Buffer terminated!')
        buffer_results.append('DONE')


class Buffer():
    def __init__(self, rasters_src, polygons, margin_around_image, buffer_front_max_size, buffer_back_max_size):

        # Initialise variables
        #   _rasters and polygons info
        self.rasters_src = rasters_src
        self.list_rasters_src = []
        for r, _, f in os.walk(self.rasters_src):
            for file in f:
                if file.endswith('.tif'):
                    file_src = r + '/' + file
                    file_src = file_src.replace('\\','/')
                    self.list_rasters_src.append(file_src)
        self.polygons = polygons

        #   _samples dimensions
        self.image_size = 512
        self.margin_around_image = margin_around_image

        #   _current sample
        self.current_pos = 0
        self.current_file_path = ""
        self.current_deltax = 0
        self.current_deltay = 0

        #   _buffers sizes
        self.buffer_front_max_size = buffer_front_max_size
        self.buffer_back_max_size = buffer_back_max_size
        self.buffer_front_size = multiprocessing.Value("i", 0)  # Integer shared variable
        self.buffer_back_size = multiprocessing.Value("i", 0)  # Integer shared variable

        #   _processes
        self.buffer_front_process = None
        self.buffer_back_process = None

        #   _lists of tasks and results
        self.manager = Manager()
        self.task_front_list = self.manager.list()
        self.result_front_list = self.manager.list()
        self.task_back_list = self.manager.list()
        self.result_back_list = self.manager.list()

        #   _create a temporary folder for the buffer
        self.temp_front_dir = tempfile.mkdtemp()
        self.temp_back_dir = tempfile.mkdtemp()

        #   _events to control the process
        self.pause_event_front = multiprocessing.Event()
        self.pause_event_back = multiprocessing.Event()

    def start(self):
        # Fill the lists for task communication
        for i in range(self.buffer_front_max_size):
            pos = (self.current_pos + i)  % len(self.polygons)  # Loop around
            self.task_front_list.append(pos)
        for i in range(1, self.buffer_back_max_size + 1):
            pos = (self.current_pos - i)  % len(self.polygons)  # Loop around
            self.task_back_list.append(pos)

        # Start the buffer processes
        self.buffer_front_process = multiprocessing.Process(
            target=clip_and_store, 
            args=[self.pause_event_front,
                  self.polygons,
                  self.margin_around_image,
                  self.list_rasters_src,
                  self.task_front_list, 
                  self.result_front_list, 
                  self.buffer_front_size,
                  self.buffer_front_max_size,
                  self.image_size,
                  self.temp_front_dir,
                  'frontward',
                  ])
        
        self.buffer_back_process = multiprocessing.Process(
            target=clip_and_store, 
            args=[self.pause_event_back,
                  self.polygons, 
                  self.margin_around_image,
                  self.list_rasters_src,
                  self.task_back_list, 
                  self.result_back_list, 
                  self.buffer_back_size,
                  self.buffer_back_max_size,
                  self.image_size,
                  self.temp_back_dir,
                  'backward',
                  ])
        
        # Start the buffers
        self.buffer_front_process.start()
        self.buffer_back_process.start()

        while len(self.result_front_list) == 0:
            sleep(0.1)
        self.current_pos, self.current_file_path, self.current_deltax, self.current_deltay = self.result_front_list[0]

    def move_forward(self):
        # Change buffers
        error_occured = False
        try:
            # Update current sample
            old_pos, old_path, new_deltax, new_deltay = self.result_front_list.pop(0)  
            self.current_pos, self.current_file_path, _, _ = self.result_front_list[0]
            self.buffer_front_size.value -= 1
            new_back_path = "no-sample"
            if old_path != 'no-sample':
                new_back_path = self.temp_back_dir + '\\' + old_path.split('\\')[-1]
            self.result_back_list.insert(0,(old_pos, new_back_path, new_deltax, new_deltay))
            self.buffer_back_size.value += 1
            if old_path != 'no-sample':
                shutil.move(old_path, new_back_path)

            if len(self.task_front_list) > 0:
                self.task_front_list.append((self.task_front_list[-1]+1) % len(self.polygons))
            else:
                self.task_front_list.append((self.result_front_list[-1][0] + 1) % len(self.polygons))
        except Exception as e:
            print("An error happened during moving forward on buffer:", e)
            print("Restarting buffer..")
            error_occured = True
        finally:
            if error_occured:
                self.reset()

    def move_backward(self):
        # change buffers
        error_occured = False
        try:
            # Update current sample
            new_pos, new_path, new_deltax, new_deltay = self.result_back_list.pop(0)
            self.current_pos = new_pos
            self.buffer_back_size.value -= 1
            new_current_path = 'no-sample'
            if new_path != 'no-sample':
                new_current_path = self.temp_front_dir + '\\' + new_path.split('\\')[-1]
            self.current_file_path = new_current_path
            self.result_front_list.insert(0,(new_pos, new_current_path, new_deltax, new_deltay))
            self.buffer_front_size.value += 1
            if new_path != 'no-sample':
                shutil.move(new_path, new_current_path)
            if len(self.task_back_list) > 0:
                self.task_back_list.append((self.task_back_list[-1] - 1) % len(self.polygons))
            else:
                self.task_back_list.append((self.result_back_list[-1][0] - 1) % len(self.polygons))
        except Exception as e:
            print("An error happened during moving forward on buffer:", e)
            print("Restarting buffer..")
            error_occured = True
        finally:
            if error_occured:
                self.reset()

    def delete_sample(self):
        try:
            _, old_path, _, _ = self.result_front_list.pop(0)  
            self.current_pos, self.current_file_path, _, _ = self.result_front_list[0]
            self.buffer_front_size.value -= 1
            if old_path != 'no-sample':
                os.remove(old_path)

            if len(self.task_front_list) > 0:
                self.task_front_list.append((self.task_front_list[-1]+1) % len(self.polygons))
            else:
                self.task_front_list.append((self.result_front_list[-1][0] + 1) % len(self.polygons))
        except Exception as e:
            print("An error happened :", e)
            print("Restarting buffer..")
            error_occured = True
        finally:
            if error_occured:
                self.reset()

    def reset(self):
        # Pauses processes
        self.pause_event_front.set()
        self.pause_event_back.set()
        self.buffer_front_process.join(timeout=2)
        self.buffer_back_process.join(timeout=2)

        # Empty temp folders
        shutil.rmtree(self.temp_front_dir)
        os.mkdir(self.temp_front_dir)
        shutil.rmtree(self.temp_back_dir)
        os.mkdir(self.temp_back_dir)
        
        # Update 
        #   _clear
        for i in range(len(self.task_front_list)):
            del self.task_front_list[0]
        for i in range(len(self.task_back_list)):
            del self.task_back_list[0]
        for i in range(len(self.result_front_list)):
            del self.result_front_list[0]
        for i in range(len(self.result_back_list)):
            del self.result_back_list[0]

        #   _create new list for task communication
        for i in range(self.buffer_front_max_size):
            pos = (self.current_pos + i)  % len(self.polygons)  # Loop around
            self.task_front_list.append(pos)
        for i in range(1, self.buffer_back_max_size + 1):
            pos = (self.current_pos - i)  % len(self.polygons)  # Loop around
            self.task_back_list.append(pos)

        #   _reset size
        self.buffer_front_size.value = 0
        self.buffer_back_size.value = 0

        # Resume processes
        self.pause_event_front.clear()
        self.pause_event_back.clear()

        # Wait for first item to be loaded
        while len(self.result_front_list) == 0:
            sleep(0.1)
        
        # Reload first itme
        self.current_pos, self.current_file_path, self.current_deltax, self.current_deltay = self.result_front_list[0]
        print("Restarted")

    def purge(self):
        # Clean up
        self.buffer_front_process.terminate()
        self.buffer_front_process.join()
        self.buffer_back_process.terminate()
        self.buffer_back_process.join()

        # Optionally delete the temp directory after use
        shutil.rmtree(self.temp_front_dir)
        shutil.rmtree(self.temp_back_dir)

    def restart(self, front_max_size, back_max_size, margin_around_image):
        try:
            self.purge()
        finally:
            #   _create a temporary folder for the buffer
            self.temp_front_dir = tempfile.mkdtemp()
            self.temp_back_dir = tempfile.mkdtemp()

            # Update 
            #   _clear
            self.task_front_list = self.manager.list()
            self.result_front_list = self.manager.list()
            self.task_back_list = self.manager.list()
            self.result_back_list = self.manager.list()

            #   _reset size
            self.buffer_front_size.value = 0
            self.buffer_back_size.value = 0

            #   _max size
            self.buffer_front_max_size = front_max_size
            self.buffer_back_max_size = back_max_size

            #   _margin
            self.margin_around_image = margin_around_image

            # Restart buffer
            self.start()

   
class Sample():
    def __init__(self):
        pass

    def get(self):
        pass

class App(tk.Tk):
    def __init__(self, raster_src, polygons_src):
        super().__init__()
        self.raster_src = raster_src
        self.polygons_src = polygons_src
        self.polygons = gpd.read_file(polygons_src)
        self.title("Sample Interface")
        self.geometry("300x200")  # Set window size

        # Center label at the top
        self.center_label = tk.Label(self, text="Center Label", font=("Arial", 14))
        self.center_label.pack(pady=10)

        # Frame for buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        # Prev and Next buttons
        self.prev_button = tk.Button(button_frame, text="Prev", command=self.on_prev)
        self.prev_button.pack(side=tk.LEFT, padx=10)

        # self.next_button = ttk.Button(button_frame, text="Next", command=lambda:test(self.next_button))
        self.next_button = tk.Button(button_frame, text="Next", command=self.on_next)
        self.next_button.pack(side=tk.LEFT, padx=10)

        # Frame for the two labels
        label_frame = tk.Frame(self)
        label_frame.pack(pady=10)

        # Side-by-side labels
        self.left_label = tk.Label(label_frame, text="Left Label", font=("Arial", 10))
        self.left_label.pack(side=tk.LEFT, padx=20)

        self.right_label = tk.Label(label_frame, text="Right Label", font=("Arial", 10))
        self.right_label.pack(side=tk.LEFT, padx=20)

        
        self.buffer = Buffer(
            rasters_src=raster_src,
            polygons=self.polygons,
            buffer_front_max_size=10,
            buffer_back_max_size=5,
            )
        self.buffer.start()
        while len(self.buffer.result_front_list) < 1:
            sleep(0.1)
        current_pos, current_file_path, _, _ = self.buffer.result_front_list[0]
        self.center_label.config(text=f"Sample {current_pos}")
        self.buffer.current_file_path = current_file_path

        # Start the update loop
        self.update_interval = 100  # 1000 milliseconds = 1 second
        self.update()

    def on_prev(self):
        # Handle "Prev" button click
        self.prev_button.config(state='disabled')
        self.next_button.config(state='disabled')
        while self.buffer.buffer_back_size.value == 1 or self.buffer.buffer_front_size.value == 1:
            sleep(0.1)
        thread = threading.Thread(target=self.buffer.move_backward)
        thread.start()

    def on_next(self):
        # Handle "Next" button click
        self.prev_button.config(state='disabled')
        self.next_button.config(state='disabled')
        while self.buffer.buffer_back_size.value == 1 or self.buffer.buffer_front_size.value == 1:
            sleep(0.1)
        thread = threading.Thread(target=self.buffer.move_forward)
        thread.start()

    def update(self):
        self.center_label.config(text=f"Sample {self.buffer.current_pos}")
        self.right_label.config(text=f"buffer : {self.buffer.buffer_front_size.value}/{self.buffer.buffer_front_max_size}")
        self.left_label.config(text=f"buffer : {self.buffer.buffer_back_size.value}/{self.buffer.buffer_back_max_size}")
        self.after(self.update_interval, self.update)

    def exit(self):
        self.buffer.purge()
        self.quit()

if __name__ == '__main__':
    # from multiprocessing import Manager
    # manager = Manager()
    # my_list = manager.list([1,2,3,4,5,6])
    # print(my_list)
    # del my_list[0]
    # print(my_list)
    # a = my_list.pop()
    # print(a)
    # b = my_list.pop(0)
    # print(b)
    # print(my_list)
    # my_list.append(12)
    # print(my_list)
    # my_list.insert(0,42)
    # print(my_list)
    # quit()
    raster_src = "./data/sources/scratch_dataset"
    polygons_src = "./data/sources/gt_tot.gpkg"

    # Create interface
    app = App(raster_src, polygons_src)

     # Override the window's close protocol
    app.protocol("WM_DELETE_WINDOW", app.exit)
    app.mainloop()
