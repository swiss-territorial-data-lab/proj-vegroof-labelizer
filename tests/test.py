import tkinter as tk

root = tk.Tk()
root.title("Frame Inside a Frame")

# Create the outer frame
outer_frame = tk.Frame(root, width=300, height=200, bg="lightblue")
outer_frame.pack(padx=10, pady=10)

# Create the inner frame
inner_frame = tk.Frame(outer_frame, width=1000, height=100, bg="lightgreen")
inner_frame.pack(pady=20)

# Add content to the inner frame (optional)
label = tk.Label(inner_frame, text="Inner Frame Content")
label.pack()

# Prevent the frames from resizing to fit their contents
outer_frame.pack_propagate(False)
inner_frame.pack_propagate(False)

root.mainloop()
