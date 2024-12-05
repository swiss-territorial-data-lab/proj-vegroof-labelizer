import numpy as np
from PIL import Image, ImageTk, ImageDraw
import rasterio
from rasterio.mask import mask
from rasterio.plot import show
from rasterio.merge import merge
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
    if len(self.list_rasters_src) == 0 or len(self.roofs_to_show) == 0:
        self.original_image = Image.open("./src/no_image.png").resize((self.img_width, self.img_height))
        self.display_image = self.original_image.copy()
        self.photo = ImageTk.PhotoImage(self.display_image)
        self.image_id = self.image.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.title.config(text="No sample to display")
        return

    # Get image from polygon and rasters
    while self.label_to_class[self.roofs_to_show.iloc[self.roof_index][self.input_class_name]] not in self.shown_cat:
        self.roof_index += 1
    roof = self.roofs_to_show.iloc[self.roof_index]
    self.egid = roof.EGID
    cat = roof[self.input_class_name]
    geometry = roof.geometry

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

    new_minx = minx - self.margin_around_image
    new_maxx = maxx + self.margin_around_image
    new_miny = miny - self.margin_around_image
    new_maxy = maxy + self.margin_around_image

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
    #geom_large = scale_geometry(geometry, xfact=5, yfact=5)

    matching_rasters = []
    matching_images = []
    out_transform = {}
    for raster_src in self.list_rasters_src:
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
        image = Image.open("./src/no_image.png").resize((self.img_width, self.img_height))
        self.photo = ImageTk.PhotoImage(image)
        self.image.config(image=self.photo)
        self.title.config(text=str(int(self.egid)) + ' - ' + self.label_to_class[cat])
        return
    
    elif len(matching_rasters) == 1:
        img_arr = matching_images[0]
    else:
        img_arr, out_transform = merge(
        sources=matching_rasters, 
        nodata=0, 
        bounds=geom_large.bounds,
        resampling=rasterio.enums.Resampling.nearest
        )
    img_arr = img_arr[1:4, ...]

    # Plot the raster and overlay the original polygon
    fig, ax = plt.subplots(figsize=(10, 10))

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
    plt.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    #   _render the figure as a NumPy array
    canvas = FigureCanvas(fig)
    canvas.draw()
    img_arr = np.frombuffer(canvas.tostring_rgb(), dtype='uint8')
    img_arr = img_arr.reshape(canvas.get_width_height()[::-1] + (3,))

    # transform if image is in 16bits:
    if img_arr.dtype == 'uint16':
        img_arr = (img_arr/np.max(img_arr) * 255).astype('uint8')

    # show results
    #img_arr = np.moveaxis(img_arr, 0, 2)
    image = Image.fromarray(img_arr)

    #   _resize image
    max_size = np.max(img_arr.shape[:2])
    ratio = self.img_width / max_size
    new_size = np.flip((np.array(img_arr.shape[0:2]) * ratio).astype(int))
    image_resized = np.array(image.resize(new_size))  # Resize for display

    #   _add padding
    min_axis = np.argmin(image_resized.shape[:2])
    min_size = np.min(image_resized.shape[:2])
    padding_size = int((self.img_width - min_size)/2)
    padding = [(padding_size, padding_size), (0, 0), (0, 0)] if min_axis == 0 else [(0, 0), (padding_size, padding_size), (0, 0)]
    padded_image = np.pad(image_resized,padding, mode='constant')
    
    # control sizes
    for ax in range(2):
        while padded_image.shape[ax] < self.img_width:
            additional_padding = np.zeros((1,padded_image.shape[1],3)) if ax == 0 else np.zeros((padded_image.shape[0], 1,3))
            padded_image = np.concatenate((padded_image, additional_padding), axis=ax)

    #   _show image and title
    self.original_image = Image.fromarray(np.uint8(padded_image))
    self.display_image = self.original_image.copy()
    self.photo = ImageTk.PhotoImage(self.display_image)
    self.image_id = self.image.create_image(0, 0, anchor=tk.NW, image=self.photo)
    self.title.config(text=str(int(self.egid)) + ' - ' + self.label_to_class[cat])

    # apply initial zoom
    self.initial_zoom = (max(deltax, deltay) + 2 * self.margin_around_image) / max(deltax, deltay)
    self.current_zoom = self.initial_zoom / 1.1
    self.update_image()


def zoom(self, event):
    # Adjust zoom level based on scroll direction
    if event.delta > 0:
        self.current_zoom *= 1.1
    elif event.delta < 0:
        self.current_zoom /= 1.1

    # Constrain zoom level
    self.current_zoom = max(1.0, min(self.current_zoom, self.initial_zoom * 1.5))

    # Get cursor position relative to the image
    cursor_x = self.image.canvasx(event.x)
    cursor_y = self.image.canvasy(event.y)

    # Adjust offsets to keep the zoom focused on the cursor position
    self.offset_x = cursor_x / self.img_width - 0.5
    self.offset_y = cursor_y / self.img_height - 0.5

    # Update the displayed image
    self.update_image()


def start_drag(self, event):
    # Record the starting position for dragging
    self.last_drag_x = event.x
    self.last_drag_y = event.y


def drag_image(self, event):
    """print(self.offset_x)
    print(self.offset_y)
    print("-"*10)"""
    # Compute the drag distance
    dx = event.x - self.last_drag_x
    dy = event.y - self.last_drag_y
    print(dx)
    print(dy)
    print("-"*10)
    # Update the offsets
    self.offset_x -= dx / self.img_width
    self.offset_y -= dy / self.img_height

    # Constrain offsets to stay within the image boundaries
    self.offset_x = max(0, min(self.offset_x, 1))
    self.offset_y = max(0, min(self.offset_y, 1))

    # Update the image position
    self.last_drag_x = event.x
    self.last_drag_y = event.y

    # Redraw the image
    self.update_image()

def update_image(self):
    # Calculate the dimensions of the cropped area
    crop_width = int(self.img_width / self.current_zoom)
    crop_height = int(self.img_height / self.current_zoom)

    # Calculate the crop box
    """center_x = int(self.offset_x * self.img_width)
    center_y = int(self.offset_y * self.img_height)
    left = max(center_x - crop_width // 2, 0)
    top = max(center_y - crop_height // 2, 0)
    right = min(left + crop_width, self.img_width)
    bottom = min(top + crop_height, self.img_height)"""
    center_x = self.img_width // 2
    center_y = self.img_height // 2
    left = center_x - crop_width // 2
    top = center_y - crop_height // 2
    right = center_x + crop_width // 2
    bottom = center_y + crop_height // 2

    # Crop and resize the image
    cropped_image = self.original_image.crop((left, top, right, bottom))
    resized_image = cropped_image.resize((self.img_width, self.img_height), Image.LANCZOS)

    # Update the canvas image
    self.display_image = resized_image
    self.tk_image = ImageTk.PhotoImage(self.display_image)
    self.image.itemconfig(self.image_id, image=self.tk_image)