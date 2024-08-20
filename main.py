import ctypes

import customtkinter as ctk
from UI import CSVViewerApp


myappid = 'personal.finance.tracker'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


if __name__ == "__main__":
    root = ctk.CTk()
    app = CSVViewerApp(root)
    root.mainloop()