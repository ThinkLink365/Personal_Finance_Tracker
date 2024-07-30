import os
import json
import shutil
from tkinter import *
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
import pandas as pd
import webbrowser
import ctypes

# Set the application user model ID for Windows
myappid = 'personal.finance.tracker'  # Change this to a unique string for your application
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

SAVED_CSVS_FILE = 'saved_csvs.json'
CSV_STORAGE_DIR = 'saved_csvs'


def open_website(url):
    webbrowser.open_new(url)


def save_csv_content(file_path, name):
    if not os.path.exists(CSV_STORAGE_DIR):
        os.makedirs(CSV_STORAGE_DIR)

    # Copy the CSV file to the dedicated storage directory
    new_file_path = os.path.join(CSV_STORAGE_DIR, f"{name}.csv")
    shutil.copy(file_path, new_file_path)

    # Save the metadata (custom name and file name) to the JSON file
    if not os.path.exists(SAVED_CSVS_FILE):
        with open(SAVED_CSVS_FILE, 'w') as f:
            json.dump({}, f)

    with open(SAVED_CSVS_FILE, 'r+') as f:
        try:
            data = json.load(f)
            if not isinstance(data, dict):
                data = {}
        except json.JSONDecodeError:
            data = {}

        data[name] = new_file_path
        f.seek(0)
        f.truncate()
        json.dump(data, f)


def load_saved_csvs():
    if not os.path.exists(SAVED_CSVS_FILE):
        return {}

    with open(SAVED_CSVS_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def delete_saved_csv(name):
    if not os.path.exists(SAVED_CSVS_FILE):
        return

    with open(SAVED_CSVS_FILE, 'r+') as f:
        try:
            data = json.load(f)
            if name in data:
                # Remove the CSV file from storage
                os.remove(data[name])
                # Remove the metadata entry
                del data[name]
                f.seek(0)
                f.truncate()
                json.dump(data, f)
        except json.JSONDecodeError:
            pass


class CSVViewerApp:
    def __init__(self, root):
        self.footer_label = None
        self.subtitle_label = None
        self.title_label = None
        self.load_button = None
        self.exit_button = None
        self.saved_csvs_button = None
        self.status_bar = None
        self.button_frame = None
        self.file_menu = None
        self.menu_bar = None
        self.csv_frame = None
        self.back_button = None
        self.save_button = None
        self.saved_csvs_frame = None
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.attributes('-fullscreen', True)
        self.root.iconbitmap('favicon.ico')
        ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue")
        self.create_widgets()

    def create_widgets(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create a menu bar using tkinter
        self.menu_bar = Menu(self.root)
        self.root.configure(menu=self.menu_bar)

        # Add static text to the application
        self.title_label = ctk.CTkLabel(self.root, text="Welcome to the Personal Finance Tracker",
                                        font=("Helvetica", 30, "bold"))
        self.title_label.pack(pady=10)

        self.subtitle_label = ctk.CTkLabel(self.root, text="Please select a CSV File to be loaded",
                                           font=("Helvetica", 20, "bold"))
        self.subtitle_label.pack(pady=10)

        # Frame for buttons
        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.pack(pady=10)

        self.load_button = ctk.CTkButton(self.button_frame, text="Load CSV", command=self.load_csv)
        self.load_button.grid(row=0, column=0, padx=0, pady=10)

        self.saved_csvs_button = ctk.CTkButton(self.button_frame, text="Saved CSVs", command=self.show_saved_csvs)
        self.saved_csvs_button.grid(row=1, column=0, padx=20, pady=10)

        self.exit_button = ctk.CTkButton(self.button_frame, text="Exit", command=self.confirm_exit)
        self.exit_button.grid(row=2, column=0, padx=20, pady=10)

        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.place(relx=0.5, rely=0.5, anchor='center')

        # Footer with clickable URL
        self.footer_label = ctk.CTkLabel(self.root, text="© Liam Ó Dubhgáin | Click here to contact me",
                                         font=("Helvetica", 20, "bold"), cursor="hand2")
        self.footer_label.pack(pady=10)
        self.footer_label.place(relx=0.5, rely=1.0, anchor=S)
        self.footer_label.bind("<Button-1>", lambda e: open_website("https://thinklink365.com/"))

    def load_csv(self):
        # Open file dialog to select CSV file
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                # Read CSV file into DataFrame
                df = pd.read_csv(file_path)
                # Display DataFrame content in the same window
                self.display_csv(df, file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def show_saved_csvs(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame to display saved CSVs
        self.saved_csvs_frame = ctk.CTkFrame(self.root)
        self.saved_csvs_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        saved_csvs = load_saved_csvs()
        if saved_csvs:
            for name, path in saved_csvs.items():
                frame = ctk.CTkFrame(self.saved_csvs_frame)
                frame.pack(pady=5, fill='x')

                button = ctk.CTkButton(frame, text=name, command=lambda p=path: self.load_saved_csv(p))
                button.pack(side=LEFT, padx=5, pady=5)

                delete_button = ctk.CTkButton(frame, text="Delete", command=lambda n=name: self.confirm_delete(n))
                delete_button.pack(side=RIGHT, padx=5, pady=5)
        else:
            no_csv_label = ctk.CTkLabel(self.saved_csvs_frame, text="No saved CSV files found.")
            no_csv_label.pack(pady=10)

        # Add a "Back" button to return to the main menu
        self.back_button = ctk.CTkButton(self.root, text="Back", command=self.create_widgets)
        self.back_button.pack(pady=10)

    def confirm_delete(self, name):
        if messagebox.askokcancel("Delete", f"Do you really want to delete '{name}'?"):
            self.delete_csv(name)

    def delete_csv(self, name):
        delete_saved_csv(name)
        self.show_saved_csvs()

    def load_saved_csv(self, file_path):
        try:
            # Read CSV file into DataFrame
            df = pd.read_csv(file_path)
            # Display DataFrame content in the same window
            self.display_csv(df, file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def display_csv(self, df, file_path):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Create a frame to display the CSV content
        self.csv_frame = ctk.CTkFrame(self.root)
        self.csv_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        text_area = Text(self.csv_frame, wrap=WORD, font=("Courier New", 10))
        text_area.insert(END, df.to_string())
        text_area.pack(padx=10, pady=10, expand=True, fill=BOTH)

        # Add a "Save CSV" button to save the CSV with a custom name
        self.save_button = ctk.CTkButton(self.root, text="Save CSV", command=lambda: self.save_csv(file_path))
        self.save_button.pack(pady=10)

        # Add a "Back" button to return to the main menu
        self.back_button = ctk.CTkButton(self.root, text="Back", command=self.create_widgets)
        self.back_button.pack(pady=10)

        # Add an "Exit" button in the CSV display view
        self.exit_button = ctk.CTkButton(self.root, text="Exit", command=self.confirm_exit)
        self.exit_button.pack(pady=10)

    def save_csv(self, file_path):
        name = simpledialog.askstring("Save CSV", "Enter a name for the CSV:")
        if name:
            save_csv_content(file_path, name)
            messagebox.showinfo("Save CSV", f"CSV saved as '{name}'.")

    def confirm_exit(self):
        if messagebox.askokcancel("Exit", "Do you really want to exit?"):
            self.root.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = CSVViewerApp(root)
    root.mainloop()
