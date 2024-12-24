import os
import tempfile
import multiprocessing
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
import shutil
from collections import deque
from multiprocessing import Manager


def clip_and_store(polygons, margin_around_image, list_rasters_src, buffer_tasks, buffer_results, buffer_size, buffer_max_size, buffer_pos, temp_dir, direction):
        """
        Worker process to clip rasters and store them in a temp folder.
        """
        while True:
            # task = self.task_queue.get()
            task = buffer_tasks.pop(0)
            if task == "STOP":
                break

            sample_pos = task
            print(f"===\n{direction} - {sample_pos}\n===")
            try:
                # Get image from polygon and rasters
                #self.sample_pos = self.dataset_to_show.index.get_loc(self.sample_index)
                # self.sample_pos = sample_pos
                sample = polygons.loc[sample_pos]
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
                    raise ValueError("Polygon did not match any raster!")
                elif len(matching_rasters) == 1:
                    img_arr = matching_images[0]
                else:
                    img_arr, out_transform = merge(
                    sources=matching_rasters, 
                    nodata=0, 
                    bounds=geom_large.bounds,
                    resampling=rasterio.enums.Resampling.nearest
                    )

                # Save image in tmp file
                img = Image.fromarray(np.moveaxis(img_arr[1:,...], 0, 2))
                temp_file_path = os.path.join(temp_dir, f"sample_{sample_pos}.png")
                img.save(temp_file_path)

                # Notify main process of the result
                # self.result_queue.put((sample_pos, temp_file_path))
                buffer_results.append((sample_pos, temp_file_path))
                # self.buffer_size.value += 1
                buffer_size.value += 1

                # print("task queue size: ", len(buffer_tasks))
                # print("result queue size: ", len(buffer_results))
                # print("buffer size :", buffer_size.value)
                # print('---')

                # if self.buffer_size >= self.buffer_max_size:
                #     break
                while buffer_size.value >= buffer_max_size:
                    sleep(0.1)

            except Exception as e:
                # self.result_queue.put((sample_pos, f"ERROR: {str(e)}"))
                buffer_results.append((sample_pos, f"ERROR: {str(e)}"))
                print("error!")
        print('done!')
        # self.result_queue.put('DONE')
        buffer_results.append('DONE')


class Buffer():
    def __init__(self, rasters_src, polygons_src):
        self.rasters_src = rasters_src
        self.polygons_src = polygons_src
        self.buffer_front_max_size = 10
        self.buffer_back_max_size = 5
        self.buffer_size = 0
        self.polygons = gpd.read_file(polygons_src)
        self.list_rasters_src = []
        self.current_pos = 0
        self.current_file_path = ""
        self.margin_around_image = 50

        self.buffer_front_size = multiprocessing.Value("i", 0)  # Integer shared variable
        self.buffer_back_size = multiprocessing.Value("i", 0)  # Integer shared variable
        self.loading_front_pos = multiprocessing.Value("i", 0)
        self.loading_back_pos = multiprocessing.Value("i", 0)
        self.buffer_front_process = None
        self.buffer_back_process = None
        self.buffer_front_max_pos = 0
        self.buffer_back_max_pos = 0

        manager = Manager()
        self.task_front_list = manager.list()
        self.result_front_list = manager.list()
        self.task_back_list = manager.list()
        self.result_back_list = manager.list()
        self.temp_front_dir = None
        self.temp_back_dir = None
    
    def start(self):
        # Setup
        for r, _, f in os.walk(self.rasters_src):
            for file in f:
                if file.endswith('.tif'):
                    file_src = r + '/' + file
                    file_src = file_src.replace('\\','/')
                    self.list_rasters_src.append(file_src)

        # Create a temporary folder for the buffer
        self.temp_front_dir = tempfile.mkdtemp()
        self.temp_back_dir = tempfile.mkdtemp()

        # Create queues for task communication
        # task_queue = multiprocessing.Queue(maxsize=self.buffer_max_size)
        # result_queue = multiprocessing.Queue(maxsize=self.buffer_max_size)

        # sample_pos = multiprocessing.Value("i", 0)  # Integer shared variable

        # self.start(task_queue, result_queue, temp_dir, buffer_size)

        # Send tasks to the buffer process
        # for pos in self.polygons.index:
        #     if self.task_queue.qsize() >= self.buffer_max_size:
        #         break
        #     self.sample_pos = pos
        #     self.task_queue.put(pos)
        for pos in list(self.polygons.index)[:self.buffer_front_max_size]:
            self.task_front_list.append(pos)
            self.buffer_front_max_pos = pos
        for pos in reversed(list(self.polygons.index)[-self.buffer_back_max_size::]):
            self.task_back_list.append(pos)
            self.buffer_back_max_pos = pos

        # Start the buffer processes
        self.buffer_front_process = multiprocessing.Process(
            target=clip_and_store, 
            args=[self.polygons, 
                  self.margin_around_image,
                  self.list_rasters_src,
                  self.task_front_list, 
                  self.result_front_list, 
                  self.buffer_front_size,
                  self.buffer_front_max_size,
                  self.loading_front_pos,
                  self.temp_front_dir,
                  'front'])
        
        self.buffer_back_process = multiprocessing.Process(
            target=clip_and_store, 
            args=[self.polygons, 
                  self.margin_around_image,
                  self.list_rasters_src,
                  self.task_back_list, 
                  self.result_back_list, 
                  self.buffer_back_size,
                  self.buffer_back_max_size,
                  self.loading_back_pos,
                  self.temp_back_dir,
                  'back'])
        
        self.buffer_front_process.start()
        self.buffer_back_process.start()

        # for raster_path in raster_files:
        #     task_queue.put((raster_path, clip_coords, buffer_size))

        # Retrieve results
        # while True:
        #     result = result_queue.get()
        #     if result == 'DONE':
        #         print("DONE!")
        #         break
        #     sample_pos, temp_file_path = result
        #     if "ERROR" in temp_file_path:
        #         print(f"Error processing {sample_pos}: {temp_file_path}")
        #     else:
        #         print(f"Clipped image stored at: {temp_file_path}")

    
    def move_forward(self):
        print("moving forward")
        # change buffers
        # pos, temp_file_path = self.result_queue.get()
        pos, temp_file_path = self.result_front_list.pop(0)
        new_current_path = self.temp_back_dir + '\\' + self.current_file_path.split('\\')[-1]
        self.result_back_list.insert(0,(self.current_pos, new_current_path))
        shutil.move(self.current_file_path, new_current_path)
        _, old_temp_file = self.result_back_list.pop()
        print
        os.remove(old_temp_file)
        self.buffer_front_max_pos += 1
        self.buffer_back_max_pos -= 1
        self.task_front_list.append(self.buffer_front_max_pos)

        # update current pos
        self.current_pos = pos
        self.current_file_path = temp_file_path
        self.buffer_front_size.value -= 1
        # self.task_queue.put(self.sample_pos)
        print(list(self.result_back_list))

    def move_backward(self):
        pass

    def create_frontward(self):
        pass

    def create_backward(self):
        pass

    def reset(self):
        pass

    def delete(self):
        pass

    def purge(self):
        pass

    def test(self):

        # Setup
        for r, _, f in os.walk(self.rasters_src):
            for file in f:
                if file.endswith('.tif'):
                    file_src = r + '/' + file
                    file_src = file_src.replace('\\','/')
                    self.list_rasters_src.append(file_src)

        # Create a temporary folder for the buffer
        temp_dir = tempfile.mkdtemp()

        # Create queues for task communication
        task_queue = multiprocessing.Queue(maxsize=self.buffer_max_size)
        result_queue = multiprocessing.Queue(maxsize=self.buffer_max_size)

        # Shared buffer size counter
        buffer_size = multiprocessing.Value("i", 0)  # Integer shared variable
        # sample_pos = multiprocessing.Value("i", 0)  # Integer shared variable

        self.start(task_queue, result_queue, temp_dir, buffer_size)

        print("STARTED")

        while True:
            print("one more!")
            result = result_queue.get()
            self.sample_pos += 1
            with buffer_size.get_lock():
                buffer_size.value -= 1
            task_queue.put(self.sample_pos)
            print("buffer_size : ", buffer_size.value)
            print("\ttask queue size: ", task_queue.qsize())
            print("\tresult queue size: ", result_queue.qsize())
            print("\tsample pos : ", self.sample_pos)
            print('---')
            print()
            sleep(5)

        # # Setup
        # raster_files = []
        # for r, d, f in os.walk(self.rasters_src):
        #     for file in f:
        #         if file.endswith('.tif'):
        #             file_src = r + '/' + file
        #             file_src = file_src.replace('\\','/')
        #             self.list_rasters_src.append(file_src)
        # # raster_files = ["path_to_raster1.tif", "path_to_raster2.tif"]  # Example raster files
        # clip_coords = (10, 10, 100, 100)  # Define your bounding box
        # buffer_size = 10  # Buffer size for clipping

        # # Create a temporary folder for the buffer
        # temp_dir = tempfile.mkdtemp()

        # # Create queues for task communication
        # task_queue = multiprocessing.Queue(maxsize=buffer_size)
        # result_queue = multiprocessing.Queue(maxsize=buffer_size)

        # # Start the buffer process
        # buffer_process = multiprocessing.Process(target=self.clip_and_store, args=(task_queue, result_queue, temp_dir))
        # buffer_process.start()

        # # Send tasks to the buffer process
        # for sample_pos in self.polygons.index:
        #     if task_queue.qsize() >= self.buffer_max_size:
        #         break
        #     task_queue.put(sample_pos)
        # # for raster_path in raster_files:
        # #     task_queue.put((raster_path, clip_coords, buffer_size))

        # # Retrieve results
        # while True:
        #     result = result_queue.get()
        #     if result == 'DONE':
        #         print("DONE!")
        #         break
        #     sample_pos, temp_file_path = result
        #     if "ERROR" in temp_file_path:
        #         print(f"Error processing {sample_pos}: {temp_file_path}")
        #     else:
        #         print(f"Clipped image stored at: {temp_file_path}")
        
        # # while True:
        # #     result_queue.
        # #     sleep(0.5)
        # # for _ in self.list_rasters:
        # #     raster_path, temp_file_path = result_queue.get()
        # #     if "ERROR" in temp_file_path:
        # #         print(f"Error processing {raster_path}: {temp_file_path}")
        # #     else:
        # #         print(f"Clipped image stored at: {temp_file_path}")

        # # Clean up
        # task_queue.put("STOP")
        # buffer_process.join()

        # # Optionally delete the temp directory after use
        # import shutil
        # shutil.rmtree(temp_dir)


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
            polygons_src=polygons_src,
            )
        self.buffer.start()
        while len(self.buffer.result_front_list) < 1:
            sleep(0.1)
        # current_pos, current_file_path = self.buffer.result_queue.get()
        current_pos, current_file_path = self.buffer.result_front_list.pop(0)
        self.center_label.config(text=f"Sample {current_pos}")
        self.buffer.current_file_path = current_file_path

        # Start the update loop
        self.update_interval = 100  # 1000 milliseconds = 1 second
        self.update()

    def on_prev(self):
        # Handle "Prev" button click
        self.center_label.config(text="Prev button clicked")

    def on_next(self):
        # Handle "Next" button click
        self.buffer.move_forward()
        #self.center_label.config(text="Next button clicked")

    def update(self):
        self.center_label.config(text=f"Sample {self.buffer.current_pos}")
        self.right_label.config(text=f"buffer : {self.buffer.buffer_front_size.value}/{self.buffer.buffer_front_max_size}")
        self.left_label.config(text=f"buffer : {self.buffer.buffer_back_size.value}/{self.buffer.buffer_back_max_size}")
        self.after(self.update_interval, self.update)

    def exit(self):
        # Clean up
        self.buffer.buffer_front_process.terminate()
        self.buffer.buffer_front_process.join()
        self.buffer.buffer_back_process.terminate()
        self.buffer.buffer_back_process.join()

        # Optionally delete the temp directory after use
        shutil.rmtree(self.buffer.temp_front_dir)
        shutil.rmtree(self.buffer.temp_back_dir)
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
