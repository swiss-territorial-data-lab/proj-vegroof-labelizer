import tkinter as tk
from PIL import Image, ImageTk

class ImageZoomApp:
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Image Zoom Example")

        # Load the image using PIL
        self.original_image = Image.open('./src/no_image.png')
        self.image_zoom_factor = 1.0  # Zoom factor
        self.image_display = self.original_image

        # Convert the image to ImageTk format
        self.tk_image = ImageTk.PhotoImage(self.image_display)

        # Create a Label to display the image
        self.label = tk.Label(root, image=self.tk_image)
        self.label.pack(fill=tk.BOTH, expand=True)

        # Bind the mouse scroll event
        self.label.bind("<MouseWheel>", self.zoom_image)

    def zoom_image(self, event):
        # Adjust zoom factor based on scroll direction
        if event.delta > 0:
            self.image_zoom_factor *= 1.1  # Zoom in
        elif event.delta < 0:
            self.image_zoom_factor /= 1.1  # Zoom out

        # Limit zoom factor to reasonable values
        self.image_zoom_factor = max(0.1, min(self.image_zoom_factor, 5.0))

        # Resize the image
        new_width = int(self.original_image.width * self.image_zoom_factor)
        new_height = int(self.original_image.height * self.image_zoom_factor)
        self.image_display = self.original_image.resize((new_width, new_height), Image.LANCZOS)

        # Update the image in the label
        self.tk_image = ImageTk.PhotoImage(self.image_display)
        self.label.config(image=self.tk_image)

# Create the main application window
root = tk.Tk()
app = ImageZoomApp(root, "your_image.jpg")  # Replace with your image path
root.mainloop()
