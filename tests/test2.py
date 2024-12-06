import tkinter as tk
from tkinter import Frame, Label

root = tk.Tk()

# Parent frame
frame_select_col_mapping = Frame(root, width=400, height=200)
frame_select_col_mapping.pack(padx=10, pady=10)

# Sub-frame
frame_select_col_mapping_sub2 = Frame(frame_select_col_mapping, width=350, height=140)
frame_select_col_mapping_sub2.pack()
frame_select_col_mapping_sub2.pack_propagate(False)

for i in range(6):
    # Child frame
    new_frame = Frame(frame_select_col_mapping_sub2, width=350, height=20)
    new_frame.pack(pady=5)
    new_frame.pack_propagate(False)

    # Label
    new_lbl = Label(new_frame, text=f"Val {i}")
    new_lbl.pack(side='left', padx=10)

    # Text widget with fixed width and height
    new_textbox = tk.Text(new_frame, width=30, height=1)  # Width in characters, height in lines
    new_textbox.pack(side='left', padx=10)

root.mainloop()
