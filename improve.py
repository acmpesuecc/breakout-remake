import os
import sys
import tkinter as tk
from PIL import Image, ImageTk

# Function to start the game
def start_game():
    # Hide the main menu window
    root.withdraw()

    # Create a new window for the game
    game_window = tk.Toplevel(root)
    game_window.title("Game Window")
    game_window.geometry("800x600")

    # Add a label to indicate the game is running
    label = tk.Label(game_window, text="Game is running...", font=("Arial", 18))
    label.pack(pady=20)

    # Function to close the game window and return to the main menu
    def close_game():
        game_window.destroy()
        root.deiconify()  # Show the main menu again

    # Add a button to go back to the menu
    exit_button = tk.Button(game_window, text="Back to Menu", command=close_game)
    exit_button.pack(pady=10)

# Function to open the settings
def open_settings():
    # Hide the main menu window
    root.withdraw()

    # Create a new window for the settings
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings Window")
    settings_window.geometry("400x300")

    # Add a label to indicate it's the settings window
    label = tk.Label(settings_window, text="Settings Window", font=("Arial", 18))
    label.pack(pady=20)

    # Function to close the settings window and return to the main menu
    def close_settings():
        settings_window.destroy()
        root.deiconify()  # Show the main menu again

    # Add a button to go back to the menu
    close_button = tk.Button(settings_window, text="Back to Menu", command=close_settings)
    close_button.pack(pady=10)

# Function to exit the application
def exit_game():
    root.destroy()

# Create the main menu window
root = tk.Tk()
root.title("Main Menu")
root.geometry("1280x720")

# Set background color for the menu bar
menu_bg_color = "black"

# Configure the menu bar
menu_bar = tk.Menu(root, background=menu_bg_color, foreground="white", 
                   activebackground="white", activeforeground=menu_bg_color)
root.config(menu=menu_bar)

# Load and display an image in the main menu
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "assets", "title.png")

# Load and resize the image using PIL
img = Image.open(image_path)
img = img.resize((500, 500))
tk_img = ImageTk.PhotoImage(img)

# Display the image in the main menu
logo_label = tk.Label(root, image=tk_img)
logo_label.pack(pady=20)

# Create a "Start Game" button
start_button = tk.Button(root, text="Start Game", command=start_game, font=("Arial", 14))
start_button.pack(pady=10)

# Add a Settings menu item
settings_menu = tk.Menu(menu_bar, tearoff=0, background=menu_bg_color, foreground="white")
menu_bar.add_cascade(label="Settings", menu=settings_menu)
settings_menu.add_command(label="Open Settings", command=open_settings)

# Add an Exit menu item
menu_bar.add_command(label="Exit", command=exit_game)

# Start the Tkinter main loop
root.mainloop()
