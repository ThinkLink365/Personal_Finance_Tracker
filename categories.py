# categories.py

from tkinter import messagebox
from tkinter import ttk

import customtkinter as ctk

from Utilises import load_category_map, add_keyword_to_category, delete_category, \
    delete_keyword_from_category


def manage_categories(app, create_widgets_callback):
    """
    Manages the categories UI and functionality.
    Provides an interface for adding, deleting, and managing keywords within categories.
    """
    clear_widgets(app.root)  # Clear widgets from the app's root

    category_map = load_category_map()

    manage_frame = ctk.CTkFrame(app.root)
    manage_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

    scrollable_frame = ctk.CTkScrollableFrame(manage_frame)
    scrollable_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

    for category, keywords in category_map.items():
        frame = ctk.CTkFrame(scrollable_frame)
        frame.pack(pady=5, padx=10, fill='x')

        category_label = ctk.CTkLabel(frame, text=category.capitalize(), font=("Helvetica", 16, "bold"))
        category_label.pack(side=ctk.LEFT, padx=10, pady=5)

        delete_category_button = ctk.CTkButton(frame, text="Delete Category",
                                               command=lambda c=category: handle_delete_category(c, app),
                                               corner_radius=8)
        delete_category_button.pack(side=ctk.RIGHT, padx=10, pady=5)

        keyword_var = ctk.StringVar(value="Select keyword")
        keyword_combobox = ttk.Combobox(frame, textvariable=keyword_var, values=keywords, state="readonly")
        keyword_combobox.pack(side=ctk.LEFT, padx=15, pady=5)

        keyword_combobox.bind("<<ComboboxSelected>>",
                              lambda event, kw_var=keyword_var, combobox=keyword_combobox: kw_var.set(combobox.get()))

        delete_keyword_button = ctk.CTkButton(frame, text="Delete Keyword",
                                              command=lambda c=category, kw_var=keyword_var:
                                              handle_delete_keyword(c, kw_var.get(), app),
                                              corner_radius=8)
        delete_keyword_button.pack(side=ctk.RIGHT, padx=10, pady=5)

    add_frame = ctk.CTkFrame(scrollable_frame)
    add_frame.pack(pady=10, padx=10, fill='x')

    new_category_label = ctk.CTkLabel(add_frame, text="New Category:", font=("Helvetica", 14))
    new_category_label.pack(side=ctk.LEFT, padx=5, pady=5)

    new_category_entry = ctk.CTkEntry(add_frame)
    new_category_entry.pack(side=ctk.LEFT, padx=5, pady=5)

    new_keyword_label = ctk.CTkLabel(add_frame, text="New Keyword:", font=("Helvetica", 14))
    new_keyword_label.pack(side=ctk.LEFT, padx=5, pady=5)

    new_keyword_entry = ctk.CTkEntry(add_frame)
    new_keyword_entry.pack(side=ctk.LEFT, padx=5, pady=5)

    add_keyword_button = ctk.CTkButton(add_frame, text="Add Keyword",
                                       command=lambda: handle_add_keyword(new_category_entry.get(),
                                                                          new_keyword_entry.get(), app),
                                       corner_radius=8)
    add_keyword_button.pack(side=ctk.LEFT, padx=10, pady=5)

    back_button = ctk.CTkButton(manage_frame, text="Back", command=create_widgets_callback, corner_radius=8)
    back_button.pack(pady=15)


def handle_add_keyword(category, keyword, app):
    """
    Handles adding a keyword to a category and refreshes the UI.
    """
    category = category.lower().strip()
    keyword = keyword.lower().strip()

    if not category or not keyword:
        messagebox.showerror("Error", "Both category and keyword must be non-empty.")
        return

    success = add_keyword_to_category(category, keyword)
    if success:
        manage_categories(app, app.create_widgets)  # Pass the app instance here to refresh the UI
    else:
        messagebox.showinfo("Info", f"The keyword '{keyword}' already exists in category '{category}'.")


def handle_delete_category(category, app):
    """
    Handles deleting a category and refreshes the UI.
    """
    if messagebox.askokcancel("Delete Category", f"Do you really want to delete the category '{category}'?"):
        success = delete_category(category)
        if success:
            manage_categories(app, app.create_widgets)  # Pass the app instance here to refresh the UI


def handle_delete_keyword(category, keyword, app):
    """
    Handles deleting a keyword from a category and refreshes the UI.
    """
    if not keyword or keyword == "Select keyword":
        messagebox.showerror("Error", "Please select a valid keyword to delete.")
        return

    success = delete_keyword_from_category(category, keyword)
    if success:
        manage_categories(app, app.create_widgets)  # Pass the app instance here to refresh the UI
    else:
        messagebox.showerror("Error", f"The keyword '{keyword}' does not exist in the category '{category}'.")


def clear_widgets(root):
    """
    Clears all the widgets from the root window.
    """
    for widget in root.winfo_children():
        widget.destroy()
