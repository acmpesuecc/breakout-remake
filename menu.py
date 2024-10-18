import os
import sys
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import json

SETTINGS_FILE = "settings.txt"  # File path for settings

# Start the game
def start_game():
    import final_1  # Load your game module here
    sys.exit()

# Load settings from the JSON file
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)  # Load settings as dictionary
    else:
        settings = {"screen_width": 1280, "screen_height": 720, "scr": "1280x720", "fps": 30}  # Default settings
    return settings

# Save updated settings to the file
def save_settings(new_resolution, new_fps):
    width, height = map(int, new_resolution.split('x'))  # Extract width and height from resolution
    settings = load_settings()  # Load existing settings

    # Update the settings
    settings["screen_width"] = width
    settings["screen_height"] = height
    settings["scr"] = new_resolution
    settings["fps"] = int(new_fps)  # Convert FPS to integer

    # Write settings back to the file
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

    messagebox.showinfo("Settings", "Settings saved successfully!")  # Show success message

# Open settings menu in the same window
def open_settings():
    settings = load_settings()  # Load current settings
    current_resolution = settings["scr"]  # Get current resolution
    current_fps = settings["fps"]  # Get current FPS

    # Create settings frame within the same window
    settings_frame = tk.Frame(root)
    settings_frame.pack(pady=20)

    def update_settings():
        selected_resolution = resolution_var.get()
        selected_fps = fps_var.get()

        save_settings(selected_resolution, selected_fps)  # Save updated settings
        settings_frame.pack_forget()  # Close settings frame after applying changes
        messagebox.showinfo("Settings", "Settings applied!")  # Show confirmation
        root.geometry(f"{settings['screen_width']}x{settings['screen_height']}")  # Adjust window size
        menu_bar.entryconfig("Settings", label=f"Settings (Res: {selected_resolution}, FPS: {selected_fps})")  # Update menu label

    # Resolution selection dropdown
    resolution_label = tk.Label(settings_frame, text="Select Resolution:")
    resolution_label.grid(row=0, column=0, padx=10, pady=5)  # Position the label

    resolution_var = tk.StringVar(value=current_resolution)
    resolutions = ["1280x720", "1366x768", "1920x1080"]  # Resolutions to choose from
    resolution_menu = tk.OptionMenu(settings_frame, resolution_var, *resolutions)
    resolution_menu.grid(row=0, column=1, padx=10, pady=5)  # Position the dropdown

    # FPS selection dropdown
    fps_label = tk.Label(settings_frame, text="Select FPS:")
    fps_label.grid(row=1, column=0, padx=10, pady=5)  # Position the label

    fps_var = tk.StringVar(value=str(current_fps))
    fps_options = ["30", "60", "120"]  # FPS options
    fps_menu = tk.OptionMenu(settings_frame, fps_var, *fps_options)
    fps_menu.grid(row=1, column=1, padx=10, pady=5)  # Position the dropdown

    # Apply button to save settings
    apply_button = tk.Button(settings_frame, text="Apply", command=update_settings)
    apply_button.grid(row=2, column=0, columnspan=2, pady=10)  # Center the button

def exit_game():
    root.destroy()  # Exit the application

# Create the main window
root = tk.Tk()

# Set window title and size
root.title("Game Menu")
root.geometry("1280x720")

# Create menu bar and configure colors
menu_bg_color = "black"
menu_bar = tk.Menu(root, background=menu_bg_color, foreground="white", activebackground="white", activeforeground=menu_bg_color)
root.config(menu=menu_bar)

# Get the absolute path to the image
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "assets", "title.png")

# Load and resize image for display
img = Image.open(image_path)
img = img.resize((500, 500))  # Adjust size as needed
tk_img = ImageTk.PhotoImage(img)

# Create a label to display the image
logo_label = tk.Label(root, image=tk_img)
logo_label.pack(pady=20)

# Create "Start Game" button
start_button = tk.Button(root, text="Start Game", command=start_game)
start_button.pack(pady=10)

# Add Settings and Exit buttons to the menu bar
settings_menu = tk.Menu(menu_bar, tearoff=0, background=menu_bg_color, foreground="white")
menu_bar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Open Settings", command=open_settings)

# Add Exit option in the menu bar
menu_bar.add_command(label="Exit", command=exit_game)

# Run the Tkinter main loop
root.mainloop()
