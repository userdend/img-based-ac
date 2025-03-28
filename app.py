import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
import os
import sqlite3

# Setup database.
conn = sqlite3.connect("app.db")
cursor  =conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS preference (id INTEGER PRIMARY KEY, name TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS sequence_order (id INTEGER PRIMARY KEY, preference_id INTEGER, path TEXT, images TEXT, FOREIGN KEY (preference_id) REFERENCES preference(id))")
conn.commit()

# Create main window.
root = tk.Tk()
root.title("Image-Based Auto Clicker")
root.geometry("400x400")
root.minsize(400, 400)
root.maxsize(400, 400)
root.resizable(False, False)

# Menu bar.
menu_bar = tk.Menu(root)

# Dictionary to store file path.
file_dict = {}

def import_image():
    file_path = filedialog.askopenfilenames(filetypes = [("Image Files", "*.*")])

    for file in file_path:
        # Get the file name.
        file_name = os.path.basename(file)

        # If file already exists.
        existing_item = sequence_order.get(0, tk.END)

        if file_name in existing_item:
            index = existing_item.index(file_name)
            sequence_order.delete(index)

        # Store the file path in dictionary.
        file_dict[file_name] = file

        # Insert the new file.
        sequence_order.insert(tk.END, file_name)

def add_preference():
    # Check if preference exists.
    def preference_exists(pref):
        preference_item = preference.get(0, tk.END)
        return pref in preference_item

    new_preference = simpledialog.askstring("New Preference", "Enter preference name:")

    if new_preference:
        new_preference = new_preference.strip()

        if new_preference:
            if preference_exists(new_preference):
                messagebox.showwarning("Warning", "Preference name already exists.")
                return

            # Add preference to the database.
            cursor.execute("INSERT INTO preference (name) VALUES (?)", (new_preference,))
            conn.commit()

            # Insert the item into Listbox.
            preference.insert(tk.END, new_preference)
        else:
            messagebox.showwarning("Warning", "Preference name cannot be empty!")

def rename_preference():
    selected_index = preference.curselection()

    if selected_index:
        index = selected_index[0]
        current_preference_name = preference.get(index)

        # Ask user for new name.
        new_preference_name = simpledialog.askstring("Rename Preference", prompt = "Enter new name:", initialvalue = current_preference_name)

        if new_preference_name:
            new_preference_name = new_preference_name.strip()

            if new_preference_name:
                # Update into database.
                cursor.execute("UPDATE preference SET name = ? WHERE name = ?", (new_preference_name, current_preference_name))
                conn.commit()

                # Update Listbox.
                preference.delete(index)
                preference.insert(index, new_preference_name)
            else:
                messagebox.showwarning("Warning", "Preference name cannot be empty!")

def delete_preference():
    selected_index = preference.curselection()
    
    if selected_index:
        # Get the preference name.
        preference_name = preference.get(selected_index)

        # Update database.
        cursor.execute("DELETE FROM preference WHERE name = ?", (preference_name,))
        conn.commit()

        # Delete from Listbox.
        preference.delete(selected_index[0])

def show_preference_context_menu(event):
    selected_index = preference.nearest(event.y)
    preference.selection_clear(0, tk.END)
    preference.selection_set(selected_index)
    preference.activate(selected_index)

    context_menu.post(event.x_root, event.y_root)
    root.after(100, lambda: root.bind("<Button-1>", lambda e: context_menu.unpost()))

# File menu.
file_menu = tk.Menu(menu_bar, tearoff = 0)
file_menu.add_command(label = "New Preference", command = add_preference)
file_menu.add_command(label = "Import Images", command = import_image)
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
            self.selection_clear(0, tk.END)
            self.selection_set(index)

    def on_release(self, event):
        # Clear the drag data upon dropping.
        self._drag_data["index"] = None

# Parent frame.
frame = tk.Frame(root)
frame.pack(pady = 20)

# Frame for Preference.
preference_frame = tk.Frame(frame)
preference_frame.pack(side = "left", padx = 10)

preference_label = tk.Label(preference_frame, text = "Preferences", font = ("Aria", 10, ""))
preference_label.pack()

preference_scrollbar = tk.Scrollbar(preference_frame, orient = "vertical")
preference = tk.Listbox(preference_frame, height = 10, width = 15, yscrollcommand = preference_scrollbar.set, selectmode=tk.SINGLE, exportselection=False)
preference_scrollbar.config(command = preference.yview)

preference.pack(side = "left")
preference_scrollbar.pack(side = "left", fill = "y")

# Context menu for preference upon right clicking.
context_menu = tk.Menu(root, tearoff = 0)
context_menu.add_command(label = "Rename", command = rename_preference)
context_menu.add_command(label = "Delete", command = delete_preference)

preference.bind("<Button-3>", show_preference_context_menu)

# Frame for sequence order.
sequence_order_frame = tk.Frame(frame)
sequence_order_frame.pack(side = "left", padx = 10)

sequence_order_label = tk.Label(sequence_order_frame, text = "Sequence Order", font = ("Aria", 10, ""))
sequence_order_label.pack()

sequence_order_scrollbar = tk.Scrollbar(sequence_order_frame, orient = "vertical")
sequence_order = DragDropListBox(sequence_order_frame, height = 10, width = 25, yscrollcommand = sequence_order_scrollbar.set, selectmode=tk.SINGLE, exportselection=False)
sequence_order_scrollbar.config(command = sequence_order.yview)

sequence_order.pack(side = "left")
sequence_order_scrollbar.pack(side = "left", fill = "y")

# Separator object.
separator = ttk.Separator(root, orient = "horizontal")
separator.pack(fill = "x")

# Get all the preference from db.
cursor.execute("SELECT name FROM preference")
for item in cursor.fetchall():
    preference.insert(tk.END, item[0])

# Root.
root.mainloop()