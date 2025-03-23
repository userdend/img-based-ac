import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

# Create main window.
root = tk.Tk()
root.title("Image-Based Auto Clicker")
root.geometry("400x400")
root.minsize(400, 400)
root.maxsize(400, 400)
root.resizable(False, False)

# Menu bar.
menu_bar = tk.Menu(root)

# File menu.
file_menu = tk.Menu(menu_bar, tearoff = 0)
file_menu.add_command(label = "New Preference", command = root.quit)
file_menu.add_command(label = "Import Images", command = root.quit)
file_menu.add_separator()
file_menu.add_command(label = "Exit", command = root.quit)

config_menu = tk.Menu(menu_bar, tearoff = 0)
config_menu.add_command(label = "Run Preference", command = root.quit)

menu_bar.add_cascade(label = "File", menu = file_menu)
menu_bar.add_cascade(label = "Config", menu = config_menu)
root.config(menu = menu_bar)

# Allow Listbox to have reorder behaviour.
class DragDropListBox(tk.Listbox):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_motion)
        self.bind("<ButtonRelease-1>", self.on_release)

        self._drag_data = {"index": None}
    
    def on_press(self, event):
        # Get item upon clicking.
        widget = event.widget
        self._drag_data["index"] = widget.nearest(event.y)
    
    def on_motion(self, event):
        # Move item in the list while dragging.
        widget = event.widget
        index = widget.nearest(event.y)

        if self._drag_data["index"] is not None and index != self._drag_data["index"]:
            # Swap items.
            item = self.get(self._drag_data["index"])
            self.delete(self._drag_data["index"])
            self.insert(index, item)

            # Update new index.
            self._drag_data["index"] = index

    def on_release(self, event):
        # Clear the drag data upon dropping.
        self._drag_data["index"] = None

# Parent frame.
frame = tk.Frame(root)
frame.pack(pady = 20)

# Frame for Preference.
preference_frame = tk.Frame(frame)
preference_frame.pack(side = "left", padx = 10)

preference_label = tk.Label(preference_frame, text = "Preferences", font = ("Aria", 10, "bold"))
preference_label.pack()

preference_scrollbar = tk.Scrollbar(preference_frame, orient = "vertical")
preference = tk.Listbox(preference_frame, height = 10, width = 20, yscrollcommand = preference_scrollbar.set)
preference_scrollbar.config(command = preference.yview)

preference.pack(side = "left")
preference_scrollbar.pack(side = "left", fill = "y")

# Frame for priority order.
priority_order_frame = tk.Frame(frame)
priority_order_frame.pack(side = "left", padx = 10)

priority_order_label = tk.Label(priority_order_frame, text = "Priority Order", font = ("Aria", 10, "bold"))
priority_order_label.pack()

priority_order_scrollbar = tk.Scrollbar(priority_order_frame, orient = "vertical")
priority_order = DragDropListBox(priority_order_frame, height = 10, width = 20, yscrollcommand = priority_order_scrollbar.set)
priority_order_scrollbar.config(command = priority_order.yview)

priority_order.pack(side = "left")
priority_order_scrollbar.pack(side = "left", fill = "y")

# Separator object.
separator = ttk.Separator(root, orient = "horizontal")
separator.pack(fill = "x")

# Add items
for i in range(1, 21):
    preference.insert(tk.END, f"Item {i}")
    priority_order.insert(tk.END, f"Value {i}")

# Root.
root.mainloop()