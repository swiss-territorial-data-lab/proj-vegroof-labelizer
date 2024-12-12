import tkinter as tk

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None

        # Bind mouse events to the widget
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        # Create the tooltip window
        if self.tip_window is not None:
            return

        x = self.widget.winfo_rootx() + 10  # Slight offset to avoid overlap
        y = self.widget.winfo_rooty() + 10
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tip_window.wm_geometry(f"+{x}+{y}")

        # Add the text to the tooltip window
        label = tk.Label(self.tip_window, text=self.text, background="yellow", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        # Destroy the tooltip window
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# Example usage
root = tk.Tk()
root.title("Tooltip Example")

# Create a label with a tooltip
label = tk.Label(root, text="Hover over me!", font=("Arial", 14))
label.pack(pady=20, padx=20)

tooltip = Tooltip(label, "This is some helpful information.")

root.mainloop()
