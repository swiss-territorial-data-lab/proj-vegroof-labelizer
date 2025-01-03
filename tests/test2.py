import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageSequence  # For resizing the GIF
import threading
import time
import numpy as np

class LoadingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Loading Icon Example")

        # Main frame
        self.main_frame = ttk.Frame(root, padding=20)
        self.main_frame.grid()

        # Loading label (for the icon)
        self.loading_label = ttk.Label(self.main_frame)
        self.loading_label.grid(row=0, column=0, pady=10)

        # Start button
        self.start_button = ttk.Button(self.main_frame, text="Start Process", command=self.start_process)
        self.start_button.grid(row=1, column=0, pady=10)

        # Prepare resized loading images
        self.frames = self.load_and_resize_gif("src/loading.gif", (100, 100))  # Resize to 100x100
        self.current_frame = 0
        self.running = False

    def load_and_resize_gif(self, filepath, size):
        """Load and resize a GIF, returning a list of PhotoImage frames."""
        image = Image.open(filepath)
        frames = []
        # Each frame can have its own palette in a GIF, so we need to store
        # them individually
        fpalettes = []
        transparency = image.info['transparency']

        for frame in ImageSequence.Iterator(image):
            frame = frame.convert("RGBA")
            frames.append(np.array(frame))
            fpalettes.append(frame.getpalette())

        images = []

        for i, frame in enumerate(frames):
            im = Image.fromarray(frame)
            im.putpalette(fpalettes[i])
            images.append(im)


        # for frame in ImageSequence.Iterator(image):
        #     # print(frame.shape)
        #     frame = frame.convert("RGBA")
        #     resized_frame = frame.resize(size, Image.Resampling.LANCZOS)  # Resize each frame
        #     tk_frame = tk.PhotoImage(resized_frame)
        #     frames.append(tk_frame)
        return images

    def start_process(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)

        # Start the animation
        self.animate_loading_icon()

        # Run the time-consuming task in a separate thread
        threading.Thread(target=self.long_task, daemon=True).start()

    def animate_loading_icon(self):
        if self.running:
            # Update the icon
            self.loading_label.config(image=self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            # Schedule the next frame
            self.root.after(100, self.animate_loading_icon)

    def long_task(self):
        # Simulate a long-running task
        time.sleep(5)  # Replace with actual task logic

        # Stop the animation when the task is done
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.loading_label.config(image="")  # Clear the icon

if __name__ == "__main__":
    root = tk.Tk()
    app = LoadingApp(root)
    root.mainloop()
