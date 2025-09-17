# main.py
import tkinter as tk
from gui import VigenereGUI

def main():
    root = tk.Tk()
    app = VigenereGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
