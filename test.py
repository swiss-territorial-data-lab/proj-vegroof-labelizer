import tkinter as tk
from tkinter import ttk

# Create the main window
root = tk.Tk()
root.geometry("300x200")

# Options for the combobox
options = ["Option 1", "Option 2", "Option 3"]

# Create the Combobox
combobox = ttk.Combobox(root, values=options)
combobox.set("Select an option")  # Default text
combobox.pack(pady=20)

# Function to execute on selection change
def on_selection(event):
    selected_value = combobox.get()
    print(f"Selected: {selected_value}")
    # You can perform additional actions here based on selected_value

# Bind the selection event to the function
combobox.bind("<<ComboboxSelected>>", on_selection)

# Run the application
root.mainloop()