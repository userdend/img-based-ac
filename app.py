import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Create main window.
root = tk.Tk()
root.title("Image-Based Auto Clicker")
root.geometry("400x400")

# Menu bar.
menu_bar = tk.Menu(root)

# File menu.
file_menu = tk.Menu(menu_bar, tearoff = 0)
file_menu.add_command(label = "Import Images", command = root.quit)
file_menu.add_separator()
file_menu.add_command(label = "Exit", command = root.quit)

menu_bar.add_cascade(label = "File", menu = file_menu)
root.config(menu = menu_bar)

# Frame for Preference and Priority Order.
frame = tk.Frame(root, bg = "#fff", width = 400, height = 200)
frame.pack(padx=10, pady=10)

# Root.
root.mainloop()