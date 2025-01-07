import numpy as np
from PIL import Image, ImageTk, ImageDraw
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.merge import merge
from time import sleep
import tkinter as tk
from shapely.affinity import scale
from shapely.geometry import Polygon, MultiPolygon
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


def scale_geometry(geometry, xfact, yfact):
    if geometry.geom_type == "MultiPolygon":
        # Scale each polygon individually and reassemble into MultiPolygon
        scaled_parts = [scale(polygon, xfact=xfact, yfact=yfact) for polygon in geometry.geoms]
        return MultiPolygon(scaled_parts)
    elif geometry.geom_type == "Polygon":
        # Scale a single polygon
        return scale(geometry, xfact=xfact, yfact=yfact)
    else:
        # If not Polygon or MultiPolygon, return the geometry unchanged
        return geometry
    
def show_image(self):
    if self.buffer:
        while self.buffer.current_file_path == "":
            sleep(0.1)
    error_happened = False
    try:
        # When no matching raster
        if len(self.list_rasters_src) == 0 or len(self.dataset_to_show) == 0 or (self.buffer and self.buffer.current_file_path == 'no-sample'):
            self.original_image = Image.open("./src/no_image.png")#.resize((self.img_width, self.img_height))
            self.display_image = self.original_image.resize((self.img_width, self.img_height))
            self.photo = ImageTk.PhotoImage(self.display_image)
            self.image_id = self.image.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.title.config(text="No sample to display")
            return

        # Show image and title
        self.original_image = Image.open(self.buffer.current_file_path)
        self.original_size = self.original_image.size
        self.display_image = self.original_image.resize((self.img_width, self.img_height))
        self.photo = ImageTk.PhotoImage(self.display_image)
        self.image_id = self.image.create_image(0, 0, anchor=tk.NW, image=self.photo)
        # cat = self.dataset_to_show.iloc[self.sample_pos][self.frac_col]
        # self.title.config(text=f"sample {self.sample_index} - {self.frac_col_val_to_lbl[str(cat)]}")

        # Apply initial zoom
        a = (max(self.buffer.current_deltax, self.buffer.current_deltay) + 2 * self.margin_around_image)
        b = max(self.buffer.current_deltax, self.buffer.current_deltay)
        self.initial_zoom = b and a / b or 0    # fancy way to do a/b and avoid divisions by 0
        self.current_zoom = max(1.0, self.initial_zoom / 1.1)
        self.offset_x = 0.5
        self.offset_y = 0.5
        self.update_image()
    except Exception as e:
        print("An error while trying to show image: ", e)
        print("Restarting buffer..")
        self.buffer.reset()
        error_happened = True
    finally:
        if error_happened:
            self.show_image()


def zoom_follow_cursor(self, event):
    #==========
    # NOT WORKING YET
    #==========

    # Store old zoom level and dimensions
    old_zoom = self.current_zoom
    old_logical_width = self.img_width / old_zoom
    old_logical_height = self.img_height / old_zoom

    # Adjust zoom level
    if event.delta > 0:
        self.current_zoom *= 1.1
    elif event.delta < 0:
        self.current_zoom /= 1.1

    # Constrain zoom level
    self.current_zoom = max(1.0, min(self.current_zoom, self.initial_zoom * 1.5))

    # Calculate the zoom factor
    zoom_factor = self.current_zoom / old_zoom

    # Update logical map dimensions
    self.logical_width = self.img_width / self.current_zoom
    self.logical_height = self.img_height / self.current_zoom

    # Get cursor position relative to the image (screen coordinates)
    cursor_x = self.image.canvasx(event.x)
    cursor_y = self.image.canvasy(event.y)

    # Convert cursor to logical coordinates
    cursor_logical_x = self.offset_x * self.img_width + cursor_x / self.img_width * old_logical_width
    cursor_logical_y = self.offset_y * self.img_height + cursor_y / self.img_height * old_logical_height

    # Calculate new offsets (relative to the full map)
    self.offset_x = (cursor_logical_x - self.logical_width / 2) / self.img_width
    self.offset_y = (cursor_logical_y - self.logical_height / 2) / self.img_height

    # Constrain offsets to keep the visible area within bounds
    self.offset_x = max(0, min(self.offset_x, 1 - self.logical_width / self.img_width))
    self.offset_y = max(0, min(self.offset_y, 1 - self.logical_height / self.img_height))

    # Update and display the resized image
    self.update_image()


def zoom(self, event):
    # Adjust zoom level
    if event.delta > 0:
        self.current_zoom *= 1.1
    elif event.delta < 0:
        self.current_zoom /= 1.1

    # Constrain zoom level
    self.current_zoom = max(1.0, min(self.current_zoom, self.initial_zoom * self.zooming_max))
  
    # Constrain offsets to stay within the image boundaries
    offset_x_max = 0.5 * (2 - 1/self.current_zoom)
    offset_y_max = 0.5 * (2 - 1/self.current_zoom)
    self.offset_x = max(0, min(self.offset_x, offset_x_max))
    self.offset_y = max(0, min(self.offset_y, offset_y_max))

    # Update and display the resized image
    self.update_image()

def start_drag(self, event):
    # Record the starting position for dragging
    self.last_drag_x = event.x
    self.last_drag_y = event.y


def drag_image(self, event):
    # Compute the drag distance
    dx = event.x - self.last_drag_x
    dy = event.y - self.last_drag_y

    #   _correct to current zoom if set so
    if self.drag_prop_to_zoom:
        dx /= (self.current_zoom * 2)
        dy /= (self.current_zoom * 2)

    # Update the offsets
    self.offset_x -= dx / self.img_width
    self.offset_y -= dy / self.img_height

    # Constrain offsets to stay within the image boundaries
    offset_x_max = 0.5 * (2 - 1/self.current_zoom)
    offset_y_max = 0.5 * (2 - 1/self.current_zoom)
    self.offset_x = max(0, min(self.offset_x, offset_x_max))
    self.offset_y = max(0, min(self.offset_y, offset_y_max))

    # Update the image position
    self.last_drag_x = event.x
    self.last_drag_y = event.y

    # Redraw the image
    self.update_image()

def update_image(self):
    # Calculate the dimensions of the cropped area
    crop_width = int(self.img_width / self.current_zoom)
    crop_height = int(self.img_height / self.current_zoom)

    ratio = self.original_size[0] / self.img_width
    # Calculate the crop box
    center_x = self.offset_x * self.img_width
    center_y = self.offset_y * self.img_height
    left = max(center_x - crop_width // 2, 0)
    top = max(center_y - crop_height // 2, 0)
    right = min(left + crop_width, self.img_width)
    bottom = min(top + crop_height, self.img_height)
    center_x = int(center_x * ratio)
    center_y = int(center_y * ratio)
    left = int(left * ratio)
    top = int(top * ratio)
    right = int(right * ratio)
    bottom = int(bottom * ratio)
    # Crop and resize the image
    cropped_image = self.original_image.crop((left, top, right, bottom))
    resized_image = cropped_image.resize((self.img_width, self.img_height), Image.LANCZOS)

    # Update the canvas image
    self.display_image = resized_image
    self.tk_image = ImageTk.PhotoImage(self.display_image)
    self.image.itemconfig(self.image_id, image=self.tk_image)