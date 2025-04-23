import tkinter as tk
from gui import FinanceTrackerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()