import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

def start_game():
    # Hide the main window
    root.withdraw()

    # Create a new window for the game
    game_window = tk.Toplevel(root)
    game_window.title("Game Window")
    game_window.geometry("800x600")

    # Add some content to the game window
    label = tk.Label(game_window, text="Game is running...")
    label.pack(pady=20)

    # Function to close the game window and bring back the main window
    def close_game():
        game_window.destroy()
        root.deiconify()

    # Add a button to exit the game and return to the main window
    exit_button = tk.Button(game_window, text="Back to Menu", command=close_game)
    exit_button.pack(pady=10)

def open_settings():
    # Hide the main window
    root.withdraw()

    # Create a new window for settings
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("400x300")

    # Add some content to the settings window
    label = tk.Label(settings_window, text="Settings Window")
    label.pack(pady=20)

    # Function to close the settings window and return to the main window
    def close_settings():
        settings_window.destroy()
        root.deiconify()

    # Add a button to exit the settings and return to the main window
    close_button = tk.Button(settings_window, text="Back to Menu", command=close_settings)
    close_button.pack(pady=10)

def exit_game():
    # Gracefully exit the application
    root.destroy()

# Create the main window
root = tk.Tk()

# Set the title of the window to an empty string
root.title("Main Menu")

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
