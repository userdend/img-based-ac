# For building GUI.
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sqlite3
import json

# For auto-clicker to function.
import os
import time
import pyautogui
import cv2
import numpy as np
import threading
import keyboard

class DragDropListBox(tk.Listbox):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app

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
        self.app.import_or_reorder()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Image-Based Auto Clicker")
        self.root.resizable(False, False)
        self.root.iconbitmap('icon.ico')

        # Variable.
        self.preference_item = []
        self.images_path = ""
        self.images = []
        self.interval_value = tk.StringVar()
        self.accuracy_value = tk.StringVar()

        # Setup database.
        self.conn = sqlite3.connect("app.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS preferences (id INTEGER PRIMARY KEY, preference TEXT, interval INTEGER, accuracy INTEGER, images TEXT)")
        self.conn.commit()

        # Setup value.
        self.cursor.execute("SELECT preference FROM preferences")
        for preference in self.cursor.fetchall():
            self.preference_item.append(preference[0])

        # Validation command to resrict input.
        self.vmcd = (self.root.register(self.validated_input_interval), '%P', '%S', '%W')
        
        # Parent frame.
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx = 10, pady = 10)

        # Images frame.
        self.images_frame = tk.Frame(self.frame)
        self.images_frame.pack(side = "left")

        self.images_scrollbar_vt = tk.Scrollbar(self.images_frame, orient = "vertical")
        self.images_scrollbar_hz = tk.Scrollbar(self.images_frame, orient = "horizontal")
        self.images_list = DragDropListBox(self.images_frame, app = self, height = 10, width = 20, xscrollcommand = self.images_scrollbar_hz.set, yscrollcommand = self.images_scrollbar_vt.set)
        self.images_scrollbar_hz.config(command = self.images_list.xview)
        self.images_scrollbar_vt.config(command = self.images_list.yview)

        self.images_scrollbar_hz.pack(side = "bottom", fill = "x")
        self.images_list.pack(side = "left")
        self.images_scrollbar_vt.pack(side = "left", fill = "y")

        # Config frame.
        self.config_frame = tk.Frame(self.frame)
        self.config_frame.pack(side = "top", padx = (10, 0))

        # Row 1.
        self.preference_label = ttk.Label(self.config_frame, text = "Preference:")
        self.preference_label.grid(row = 1, column = 0, sticky = "w", pady = (0, 10))

        self.preference = ttk.Combobox(self.config_frame, values = self.preference_item, state = "readonly")
        self.preference.set("Select")
        self.preference.grid(row = 1, column = 1, sticky = "nsew", pady = (0, 10))
        self.preference.bind("<<ComboboxSelected>>", self.upon_preference_selected)

        # Row 2.
        self.interval_label = ttk.Label(self.config_frame, text = "Interval (ms):")
        self.interval_label.grid(row = 2, column = 0, sticky = "w", pady = (0, 10))

        self.interval = ttk.Spinbox(self.config_frame, from_ = 0, to = 100000, validate = "key", validatecommand = self.vmcd, textvariable = self.interval_value)
        self.interval.grid(row = 2, column = 1, sticky = "w", pady = (0, 10))
        self.interval.set(1000)

        # Row 3.
        self.accuracy_label = ttk.Label(self.config_frame, text = "Accuracy (%):")
        self.accuracy_label.grid(row = 3, column = 0, sticky = "w", pady = (0, 10))

        self.accuracy = ttk.Spinbox(self.config_frame, from_ = 1, to = 100, validate = "key", validatecommand = self.vmcd, textvariable = self.accuracy_value)
        self.accuracy.grid(row = 3, column = 1, sticky = "w", pady = (0, 10))
        self.accuracy.set(80)

        # Row 4.
        self.btn_new_preference = ttk.Button(self.config_frame, text = "New Preference", command = self.add_preference)
        self.btn_new_preference.grid(row = 4, column = 0, sticky = "nsew", padx = (0, 10), pady = (0, 10))

        self.btn_import_images = ttk.Button(self.config_frame, text = "Import Images", state = "disabled", command = self.import_images)
        self.btn_import_images.grid(row = 4, column = 1, sticky = "nsew", pady = (0, 10))
        
        # Row 5.
        self.btn_start = ttk.Button(self.config_frame, text = "Start", command = self.upon_start_clicked)
        self.btn_start.grid(row = 5, column = 0, columnspan = 2, sticky = "nsew", pady = (0, 10))

        # Row 6.
        self.info = ttk.Label(self.config_frame, text = "\u2139 Drag and drop to reorder items.\n\u2139 Press ESC to stop the program.")
        self.info.grid(row = 6, column = 0, columnspan = 2)

    def validated_input_interval(self, user_input, new_value, widget_name):
        # Allow empty value or only digits as valid input.
        if new_value == '' or new_value.isdigit():
            try:
                # Get value from the Spinbox.
                min = int(self.root.nametowidget(widget_name).cget('from'))
                max = int(self.root.nametowidget(widget_name).cget('to'))

                # Check input range.
                if user_input and int(user_input) not in range(min, max + 1):
                    return False
                return True
            except ValueError:
                return False
        return False

    def add_preference(self):
        def preference_exists(item):
            return item in self.preference_item
        
        new_preference = simpledialog.askstring("New Preference", "Enter Name:")

        if new_preference:
            new_preference = new_preference.strip()

            if new_preference:
                if preference_exists(new_preference):
                    messagebox.showwarning("Warning", "Preference name already in used.")
                    return
                
                self.preference_item.append(new_preference)
                self.preference['values'] = self.preference_item

                # Update database.
                self.cursor.execute("INSERT INTO preferences (preference, interval, accuracy) VALUES (?, ?, ?)", (new_preference, 1000, 80))
                self.conn.commit()
                
            else:
                messagebox.showwarning("Warning", "Name cannot be empty.")
    
    def upon_preference_selected(self, event):
        if self.preference.get() != "Select":
            # Enable import image button.
            self.btn_import_images.config(state = "normal")

            # Read from database.
            self.cursor.execute("SELECT interval, accuracy, images FROM preferences WHERE preference = ?", (self.preference.get(),))
            result = self.cursor.fetchone()

            # Clear Listbox and insert the image.
            self.images_list.delete(0, "end")

            if result:
                interval, accuracy, images = result
                self.interval.set(interval)
                self.accuracy.set(accuracy)
                
                if images:
                    for image in json.loads(images):
                        self.images_list.insert(tk.END, image)
            
            self.images_list.xview_moveto(1)
        else:
            self.btn_import_images.config(state = "disabled")

    def import_images(self):
        file_paths = filedialog.askopenfilenames(filetypes = [("Image Files", "*.*")])

        for file in file_paths:
            if os.path.isfile(file) and file.endswith(('png', 'jpg', 'jpeg', 'gif', 'PNG', 'JPG', 'JPEG', 'GIF')):
                if file not in self.images:
                    self.images.append(file)
            else:
                messagebox.showwarning("Warning", f"Invalid file: {file}")

        # Clear Listbox and insert the image.
        self.images_list.delete(0, "end")

        for image in self.images:
            self.images_list.insert("end", image)
        
        self.import_or_reorder()

    def import_or_reorder(self):
        images = []
        for index in range(self.images_list.size()):
            value = self.images_list.get(index)
            images.append(value)

        self.cursor.execute("UPDATE preferences SET images = ? WHERE preference = ?", (json.dumps(images), self.preference.get()))
        self.conn.commit()

    def upon_start_clicked(self):
        self.btn_start.config(state = "disabled")
    
        interval_value = int(self.interval_value.get())
        accuracy_value = int(self.accuracy_value.get())

        self.cursor.execute("UPDATE preferences SET interval = ?, accuracy = ? WHERE preference = ?", (interval_value, accuracy_value, self.preference.get()))
        self.conn.commit()

        interval_value = interval_value / 1000
        accuracy_value = accuracy_value / 100

        self.stop_loop = False

        # Start a separate thread for detecting ESC key press
        threading.Thread(target = self.monitor_esc_program, daemon = True).start()

        # Start auto-clicker on another thread.
        threading.Thread(target = self.start_auto_click, args = (interval_value, accuracy_value), daemon = True).start()
    
    def monitor_esc_program(self):
        while not self.stop_loop:
            if keyboard.is_pressed('esc'):
                self.stop_loop = True
                self.update_ui_on_stop()
                return
            
            time.sleep(0.1)

    def start_auto_click(self, iv, av):
        while not self.stop_loop:
            for image_path in self.images_list.get(0, tk.END):
                self.find_and_click_images(image_path, iv, av)
            
            time.sleep(iv)  # Delay before searching again.

    def find_and_click_images(self, image_path, iv, av):
        # Disable PyAutoGUI failsafe (Only if needed).
        pyautogui.FAILSAFE = False

        # Set confidence threshold for image matching.
        CONFIDENCE_THRESHOLD = av  # Adjust based on accuracy needed.

        # Take a screenshot
        screen = pyautogui.screenshot()
        screen = np.array(screen)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)  # Convert to grayscale.

        # Load the template image.
        template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

        if template is None:
            print(f"[ERROR] Cannot load template: {image_path}")
            return

        # Get template size.
        h, w = template.shape[:2]

        # Match template.
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= CONFIDENCE_THRESHOLD)

        clicked_positions = set()  # Prevent clicking the same spot multiple times.

        for pt in zip(*locations[::-1]):  # Iterate through matched locations.
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2

            # Avoid duplicate clicks (if images are close together).
            if any(abs(center_x - x) < 10 and abs(center_y - y) < 10 for x, y in clicked_positions):
                continue

            clicked_positions.add((center_x, center_y))

            # Move and click
            pyautogui.moveTo(center_x, center_y, duration=0.02)
            pyautogui.click()
            pyautogui.moveTo(0, 0, 0)
            time.sleep(iv)  # Delay to prevent excessive clicking.

    def update_ui_on_stop(self):
        self.root.after(0, lambda: self.btn_start.config(state = "normal"))
        self.root.after(0, lambda: messagebox.showinfo("Info", "Auto-clicker stopped."))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()