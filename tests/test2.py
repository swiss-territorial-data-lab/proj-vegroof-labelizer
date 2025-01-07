import tkinter as tk

def disable_menu_items(menu):
    # Disable all items in the menu
    for i in range(menu.index('end') + 1):  # Iterate through all items
        menu.entryconfig(i, state="disabled")

def enable_menu_items(menu):
    # Enable all items in the menu
    for i in range(menu.index('end') + 1):  # Iterate through all items
        menu.entryconfig(i, state="normal")

root = tk.Tk()

# Create a Menu
menubar = tk.Menu(root)
file_menu = tk.Menu(menubar, tearoff=0)

# Add items to the file menu
file_menu.add_command(label="New")
file_menu.add_command(label="Open")
file_menu.add_command(label="Save")

# Add the file menu to the menubar
menubar.add_cascade(label="File", menu=file_menu)

# Set the menubar for the window
root.config(menu=menubar)

# Button to disable the menu items
disable_button = tk.Button(root, text="Disable Menu Items", command=lambda: disable_menu_items(file_menu))
disable_button.pack(pady=10)

# Button to enable the menu items again
enable_button = tk.Button(root, text="Enable Menu Items", command=lambda: enable_menu_items(file_menu))
enable_button.pack(pady=10)

root.mainloop()
