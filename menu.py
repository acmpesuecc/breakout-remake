import os,sys 
import tkinter as tk
from PIL import Image, ImageTk
from subprocess import Popen
def start_game():
    # Add the code to start your game here
    import final_1
    sys.exit()
def open_settings():
    # Add code to open settings window or perform settings actions
    print("Open Settings")

def exit_game():
    # Add code to gracefully exit the application
    root.destroy()

# Create the main window
root = tk.Tk()

# Set the title of the window to an empty string
root.title("")

# Set the background color of the menu bar
menu_bg_color = "black"

# Customize the appearance of the menu bar
menu_bar = tk.Menu(root, background=menu_bg_color, foreground="white",
                   activebackground="white", activeforeground=menu_bg_color)
root.config(menu=menu_bar)

# Get the absolute path to the alpha image
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "assets", "title.png")

# Open the PNG image with PIL and convert it to a format compatible with Tkinter
img = Image.open(image_path)
img = img.resize((500, 500))
tk_img = ImageTk.PhotoImage(img)

# Create a label to display the image
logo_label = tk.Label(root, image=tk_img)
logo_label.pack(pady=20)

# Set the window size to match the image size
window_width = 1280
window_height = 720
root.geometry(f"{window_width}x{window_height}")

# Create a Start Game button
start_button = tk.Button(root, text="Start Game", command=start_game)
start_button.pack(pady=10)
# Add Settings and Exit buttons to the menu bar
settings_menu = tk.Menu(menu_bar, tearoff=0, background=menu_bg_color, foreground="white")
menu_bar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Open Settings", command=open_settings)

menu_bar.add_command(label="Exit", command=exit_game)

# Run the Tkinter main loop
root.mainloop()
