import tkinter as tk
from tkinter import ttk

def set_widget_state(widget, state):
    """
    Recursively sets the state of all widgets within a parent widget.
    
    Args:
        widget: The parent widget (e.g., a frame).
        state: The desired state ("disabled" or "normal").
    """
    # Loop through all child widgets of the current widget
    for child in widget.winfo_children():
        # If the widget supports a 'state' attribute, set it
        print(child)
        if isinstance(child, (tk.Entry, tk.Button, ttk.Combobox, ttk.Checkbutton, ttk.Radiobutton, tk.Text)):
            child.configure(state=state)
        # If the widget is a container (e.g., Frame), recurse into it
        elif isinstance(child, tk.Frame):
            set_widget_state(child, state)

# Example Usage
root = tk.Tk()
root.title("Recursive Disable Example")

# Parent frame
parent_frame = tk.Frame(root, relief=tk.SUNKEN, borderwidth=2, padx=10, pady=10)
parent_frame.pack(padx=20, pady=20)

# Create nested frames with widgets
for i in range(3):
    sub_frame = tk.Frame(parent_frame, relief=tk.RIDGE, borderwidth=2, padx=5, pady=5)
    sub_frame.pack(pady=10, fill="x")
    tk.Label(sub_frame, text=f"Frame {i+1}").pack(side="left")
    tk.Entry(sub_frame).pack(side="left", padx=5)
    tk.Button(sub_frame, text="Click Me").pack(side="left", padx=5)

# Add a button to disable all widgets in the parent frame
disable_button = tk.Button(root, text="Disable All", command=lambda: set_widget_state(parent_frame, "disabled"))
disable_button.pack(pady=10)

# Add a button to enable all widgets in the parent frame
enable_button = tk.Button(root, text="Enable All", command=lambda: set_widget_state(parent_frame, "normal"))
enable_button.pack(pady=10)

root.mainloop()
