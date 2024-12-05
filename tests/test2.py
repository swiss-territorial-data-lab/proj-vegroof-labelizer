import tkinter as tk
from PIL import Image, ImageTk

class ImageZoomApp:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Interactive Zoom Example")

        # Load the image
        self.original_image = Image.open(image_path)
        self.current_zoom = 1.0  # Initial zoom level
        self.offset_x = 0
        self.offset_y = 0

        # Get the image dimensions
        self.img_width, self.img_height = self.original_image.size

        # Create a canvas to display the image
        self.canvas = tk.Canvas(root, width=self.img_width, height=self.img_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Convert the image to ImageTk format
        self.display_image = self.original_image.copy()
        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        # Bind mouse scroll and movement events
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<B1-Motion>", self.drag_image)
        self.canvas.bind("<Button-1>", self.start_drag)

        # Variables to handle dragging
        self.last_drag_x = 0
        self.last_drag_y = 0

    def zoom(self, event):
        # Adjust zoom level based on scroll direction
        if event.delta > 0:
            self.current_zoom *= 1.1
        elif event.delta < 0:
            self.current_zoom /= 1.1

        # Constrain zoom level
        self.current_zoom = max(1.0, min(self.current_zoom, 5.0))

        # Get cursor position relative to the image
        cursor_x = self.canvas.canvasx(event.x)
        cursor_y = self.canvas.canvasy(event.y)

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
        # Compute the drag distance
        dx = event.x - self.last_drag_x
        dy = event.y - self.last_drag_y

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
        center_x = int(self.offset_x * self.img_width)
        center_y = int(self.offset_y * self.img_height)
        left = max(center_x - crop_width // 2, 0)
        top = max(center_y - crop_height // 2, 0)
        right = min(left + crop_width, self.img_width)
        bottom = min(top + crop_height, self.img_height)

        # Crop and resize the image
        cropped_image = self.original_image.crop((left, top, right, bottom))
        resized_image = cropped_image.resize((self.img_width, self.img_height), Image.LANCZOS)

        # Update the canvas image
        self.display_image = resized_image
        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas.itemconfig(self.image_id, image=self.tk_image)

# Create the application window
root = tk.Tk()
app = ImageZoomApp(root, "./src/no_image.png")  # Replace with your image path
root.mainloop()
