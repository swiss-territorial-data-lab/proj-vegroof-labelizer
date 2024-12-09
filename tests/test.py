import tkinter as tk

# Function to select all text when the Text widget gains focus
def select_all(event):
    # Select all text
    event.widget.focus_set()  # Ensure the widget has focus
    event.widget.tag_add("sel", "1.0", "end-1c")  # Add selection tag
    return "break"  # Prevent default behavior

# Function to move focus to the next widget
def focus_next(event):
    event.widget.tk_focusNext().focus()
    return "break"

# Function to move focus to the previous widget with Shift+Tab
def focus_previous(event):
    event.widget.tk_focusPrev().focus()
    return "break"

# Create the main Tkinter window
root = tk.Tk()

# Create multiple Text widgets
text1 = tk.Text(root, height=5, width=40)
text2 = tk.Text(root, height=5, width=40)
text3 = tk.Text(root, height=5, width=40)

# Add some default text
text1.insert("1.0", "This is Text 1.")
text2.insert("1.0", "This is Text 2.")
text3.insert("1.0", "This is Text 3.")

# Pack the widgets
text1.pack(pady=5)
text2.pack(pady=5)
text3.pack(pady=5)

# Bind the <<FocusIn>> event to select all text
text1.bind("<FocusIn>", select_all)
text2.bind("<FocusIn>", select_all)
text3.bind("<FocusIn>", select_all)

# Bind the <Tab> key to focus_next function
text1.bind("<Tab>", focus_next)
text2.bind("<Tab>", focus_next)
text3.bind("<Tab>", focus_next)

# Bind Shift+Tab to move focus backward
text1.bind("<Shift-Tab>", focus_previous)
text2.bind("<Shift-Tab>", focus_previous)
text3.bind("<Shift-Tab>", focus_previous)

# Run the Tkinter event loop
root.mainloop()
