import tkinter as tk
from tkinter import PhotoImage
import final_1
import yes
def open_game_menu():
    # Destroy the current window
    root.destroy()

    # Create a new window for the game menu
    game_menu = tk.Tk()
    game_menu.title("Game Menu")
    game_menu.geometry('800x600')
    game_menu.configure(bg="black")

    # Load images for buttons
    image_pong = tk.PhotoImage(file="assets/pong1.png")
    image_brick_slayer = tk.PhotoImage(file="assets/break1.png")

    # Create buttons for games
    button_pong = tk.Button(game_menu, image=image_pong, command=start_pong, bd=0, highlightthickness=0)
    button_pong.image = image_pong
    button_pong.pack(pady=20)

    button_brick_slayer = tk.Button(game_menu, image=image_brick_slayer, command=start_brick_slayer, bd=0, highlightthickness=0)
    button_brick_slayer.image = image_brick_slayer
    button_brick_slayer.pack(pady=20)

    # Create an Exit button
    button_exit = tk.Button(game_menu, text="Exit", command=game_menu.destroy, font=('Helvetica', 16), bg="red", fg="white")
    button_exit.pack(pady=20)

def start_pong():
    # Replace this with the code to start the Pong game
    final_1.main()

def start_brick_slayer():
    # Replace this with the code to start the Brick Slayer game
    yes.play()

# Create the main window
root = tk.Tk()
root.title("Game Launcher")
root.geometry("600x400")
root.configure(bg="black")

# Load images for the Start and Exit buttons
image_start = tk.PhotoImage(file="assets/start.png")
image_exit = tk.PhotoImage(file="assets/menuexit.png")

# Create buttons for the main menu
button_start = tk.Button(root, image=image_start, command=open_game_menu, bd=0, highlightthickness=0)
button_start.image = image_start
button_start.pack(pady=50)

button_exit = tk.Button(root, image=image_exit, command=root.destroy, bd=0, highlightthickness=0)
button_exit.image = image_exit
button_exit.pack(pady=50)

# Run the Tkinter event loop
root.mainloop()
