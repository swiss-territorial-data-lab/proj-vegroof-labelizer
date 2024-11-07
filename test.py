import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Fixed Width Combobox Example")

# Create a frame to hold the label and combobox
frame = tk.Frame(root, width=300, height=50)
frame.pack(padx=10, pady=10)
frame.pack_propagate(False)

# Create a label
label = tk.Label(frame, text="Choose option:")
label.pack(side="left", padx=5)

# Create a combobox with a fixed width
options = ["Option 1", "Option 2", "Option 3"]
combobox = ttk.Combobox(frame, values=options, width=10)  # Width in characters
combobox.pack(side="right", padx=5)

root.mainloop()
