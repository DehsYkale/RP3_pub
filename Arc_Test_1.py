import tkinter as tk
from tkinter import messagebox

def main():
    # Create a root window (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Display the message box
    messagebox.showinfo("Greeting", "Hello World")

    # Destroy the root window
    root.destroy()

if __name__ == "__main__":
    main()
