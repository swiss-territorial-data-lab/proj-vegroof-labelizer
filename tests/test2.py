import tkinter as tk
from tkinter import ttk
import threading
import time

def long_running_task(button):
    # Simulate a long-running task
    print("Task started")
    time.sleep(5)
    print("Task completed")
    # Re-enable the button after task completion
    button.config(state='normal')

def on_button_click(button):
    # Disable the button to prevent spamming
    button.config(state='disabled')
    # Start the long-running task in a separate thread
    thread = threading.Thread(target=long_running_task, args=(button,))
    thread.start()

# Create the main Tkinter application
root = tk.Tk()
root.title("Button Disable Example")

# Create a button
my_button = ttk.Button(root, text="Run Task", command=lambda: on_button_click(my_button))
my_button.pack(pady=20)

# Start the Tkinter event loop
root.mainloop()
