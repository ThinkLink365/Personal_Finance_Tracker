import customtkinter as ctk
from tkinter import Menu, Text, WORD, filedialog, messagebox, simpledialog, ttk
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Utilises import categorize, save_csv_content, load_saved_csvs, delete_saved_csv, add_keyword_to_category, \
    delete_category, delete_keyword_from_category, open_website, load_category_map


class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.attributes('-fullscreen', True)
        self.root.iconbitmap('favicon.ico')
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.create_widgets()

    def create_widgets(self):
        self.clear_widgets()

        self.menu_bar = Menu(self.root)
        self.root.configure(menu=self.menu_bar)

        self.title_label = ctk.CTkLabel(self.root, text="Welcome to the Personal Finance Tracker",
                                        font=("Helvetica", 30, "bold"))
        self.title_label.pack(pady=10)

        self.subtitle_label = ctk.CTkLabel(self.root, text="Please select CSV files to be loaded",
                                           font=("Helvetica", 20, "bold"))
        self.subtitle_label.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.pack(pady=10)

        self.load_button = ctk.CTkButton(self.button_frame, text="Load CSVs", command=self.load_csv)
        self.load_button.grid(row=0, column=0, padx=0, pady=10)

        self.saved_csvs_button = ctk.CTkButton(self.button_frame, text="Saved CSVs", command=self.show_saved_csvs)
        self.saved_csvs_button.grid(row=1, column=0, padx=20, pady=10)

        self.manage_categories_button = ctk.CTkButton(self.button_frame, text="Manage Categories",
                                                      command=self.manage_categories)
        self.manage_categories_button.grid(row=2, column=0, padx=20, pady=10)

        self.exit_button = ctk.CTkButton(self.button_frame, text="Exit", command=self.confirm_exit)
        self.exit_button.grid(row=3, column=0, padx=20, pady=10)

        self.button_frame.grid_columnconfigure(0, weight=1)
        self.button_frame.grid_columnconfigure(1, weight=1)
        self.button_frame.grid_columnconfigure(2, weight=1)
        self.button_frame.place(relx=0.5, rely=0.5, anchor='center')

        self.footer_label = ctk.CTkLabel(self.root, text="© Liam Ó Dubhgáin | Click here to contact me",
                                         font=("Helvetica", 20, "bold"), cursor="hand2")
        self.footer_label.pack(pady=10)
        self.footer_label.place(relx=0.5, rely=1.0, anchor='s')
        self.footer_label.bind("<Button-1>", lambda e: open_website("https://thinklink365.com/"))

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def manage_categories(self):
        self.clear_widgets()
        category_map = load_category_map()

        self.manage_frame = ctk.CTkFrame(self.root)
        self.manage_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        scrollable_frame = ctk.CTkScrollableFrame(self.manage_frame)
        scrollable_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        for category, keywords in category_map.items():
            frame = ctk.CTkFrame(scrollable_frame)
            frame.pack(pady=5, padx=10, fill='x')

            category_label = ctk.CTkLabel(frame, text=category.capitalize(), font=("Helvetica", 16, "bold"))
            category_label.pack(side=ctk.LEFT, padx=10, pady=5)

            delete_category_button = ctk.CTkButton(frame, text="Delete Category",
                                                   command=lambda c=category: self.delete_category(c),
                                                   corner_radius=8)
            delete_category_button.pack(side=ctk.RIGHT, padx=10, pady=5)

            keyword_var = ctk.StringVar(value="Select keyword")
            keyword_combobox = ttk.Combobox(frame, textvariable=keyword_var, values=keywords, state="readonly")
            keyword_combobox.pack(side=ctk.LEFT, padx=15, pady=5)

            keyword_combobox.bind("<<ComboboxSelected>>",
                                  lambda event, kw_var=keyword_var, combobox=keyword_combobox: kw_var.set(
                                      combobox.get()))

            delete_keyword_button = ctk.CTkButton(
                frame,
                text="Delete Keyword",
                command=lambda c=category, kw_var=keyword_var: self.delete_keyword(c, kw_var.get()),
                corner_radius=8
            )
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
                                           command=lambda: self.add_keyword(new_category_entry.get(),
                                                                            new_keyword_entry.get()),
                                           corner_radius=8)
        add_keyword_button.pack(side=ctk.LEFT, padx=10, pady=5)

        self.back_button = ctk.CTkButton(self.manage_frame, text="Back", command=self.create_widgets, corner_radius=8)
        self.back_button.pack(pady=15)

    def add_keyword(self, category, keyword):
        category = category.lower().strip()
        keyword = keyword.lower().strip()

        if not category or not keyword:
            messagebox.showerror("Error", "Both category and keyword must be non-empty.")
            return

        success = add_keyword_to_category(category, keyword)
        if success:
            self.manage_categories()
        else:
            messagebox.showinfo("Info", f"The keyword '{keyword}' already exists in category '{category}'.")

    def delete_category(self, category):
        if messagebox.askokcancel("Delete Category", f"Do you really want to delete the category '{category}'?"):
            success = delete_category(category)
            if success:
                self.manage_categories()

    def delete_keyword(self, category, keyword):
        if not keyword or keyword == "Select keyword":
            messagebox.showerror("Error", "Please select a valid keyword to delete.")
            return

        success = delete_keyword_from_category(category, keyword)
        if success:
            self.manage_categories()
        else:
            messagebox.showerror("Error", f"The keyword '{keyword}' does not exist in the category '{category}'.")

    def load_csv(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if file_paths:
            for file_path in file_paths:
                try:
                    df = pd.read_csv(file_path)
                    self.process_csv(df, file_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load CSV file '{file_path}': {e}")

    def process_csv(self, df, file_path):
        if 'Amount' in df.columns:
            required_columns = ['Started Date', 'Description', 'Amount', 'Balance']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = '' if col != 'Amount' else 0
            df = df[required_columns]
            df['Debit'] = df.apply(lambda row: row['Amount'] if row['Amount'] < 0 else 0, axis=1)
            df['Credit'] = df.apply(lambda row: row['Amount'] if row['Amount'] > 0 else 0, axis=1)
            df['Category'] = df.apply(lambda row: categorize(row['Description']), axis=1)

        elif 'Debit Amount' in df.columns and 'Credit Amount' in df.columns:
            required_columns = ['Posted Transactions Date', 'Description1', 'Debit Amount', 'Credit Amount', 'Balance']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = '' if col not in ['Debit Amount', 'Credit Amount'] else 0
            df = df[required_columns]
            df['Debit'] = df['Debit Amount']
            df['Credit'] = df['Credit Amount']
            df['Category'] = df.apply(lambda row: categorize(row['Description1']), axis=1)
            df.rename(columns={'Posted Transactions Date': 'Started Date', 'Description1': 'Description'}, inplace=True)

        else:
            messagebox.showerror("Error",
                                 "CSV file must contain 'Amount' column or both 'Debit Amount' and 'Credit Amount' columns.")
            return

        debits_df = df[df['Debit'] != 0]
        credits_df = df[df['Credit'] != 0]

        self.show_text_frame(debits_df, credits_df, df, file_path)

    def show_text_frame(self, debits_df, credits_df, df, file_path):
        self.clear_widgets()

        self.text_frame = ctk.CTkFrame(self.root)
        self.text_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        text_area = Text(self.text_frame, wrap=WORD, font=("Courier New", 14))

        text_area.insert("end", "Debits:\n")
        if not debits_df.empty:
            text_area.insert("end",
                             debits_df[['Started Date', 'Description', 'Debit', 'Balance', 'Category']].to_string(
                                 index=False))
        else:
            text_area.insert("end", "No debits found.\n")

        text_area.insert("end", "\nCredits:\n")
        if not credits_df.empty:
            text_area.insert("end",
                             credits_df[['Started Date', 'Description', 'Credit', 'Balance', 'Category']].to_string(
                                 index=False))
        else:
            text_area.insert("end", "No credits found.\n")

        total_debits = debits_df['Debit'].sum()
        total_credits = credits_df['Credit'].sum()
        ending_balance = df['Balance'].iloc[-1] if 'Balance' in df.columns else 0

        text_area.insert("end", "\n\nAnalysis Results:\n")
        text_area.insert("end", f"Total Debits: {total_debits}\n")
        text_area.insert("end", f"Total Credits: {total_credits}\n")
        text_area.insert("end", f"Ending Balance: {ending_balance}\n")

        text_area.config(state="disabled")

        text_area.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        self.switch_to_graph_button = ctk.CTkButton(self.text_frame, text="Show Graphs",
                                                    command=lambda: self.show_graph_frame(debits_df, credits_df, df,
                                                                                          file_path))
        self.switch_to_graph_button.pack(pady=10)

        self.save_button = ctk.CTkButton(self.text_frame, text="Save CSV", command=lambda: save_csv_content(file_path,
                                                                                                            simpledialog.askstring(
                                                                                                                "Save CSV",
                                                                                                                "Enter a name for the CSV:")))
        self.save_button.pack(pady=10)

        self.back_button = ctk.CTkButton(self.text_frame, text="Back", command=self.create_widgets)
        self.back_button.pack(pady=10)

    def show_graph_frame(self, debits_df, credits_df, df, file_path):
        self.clear_widgets()

        self.graph_frame = ctk.CTkFrame(self.root)
        self.graph_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        button_frame = ctk.CTkFrame(self.graph_frame)
        button_frame.pack(pady=10)

        self.debits_button = ctk.CTkButton(button_frame, text="Show Debits Graph",
                                           command=lambda: self.plot_graphs(debits_df, credits_df,
                                                                            plot_type='debits'))
        self.debits_button.grid(row=0, column=0, padx=5, pady=10)

        self.credits_button = ctk.CTkButton(button_frame, text="Show Credits Graph",
                                            command=lambda: self.plot_graphs(debits_df, credits_df,
                                                                             plot_type='credits'))
        self.credits_button.grid(row=0, column=1, padx=5, pady=10)

        self.switch_to_text_button = ctk.CTkButton(button_frame, text="Show Text",
                                                   command=lambda: self.show_text_frame(debits_df, credits_df, df,
                                                                                        file_path))
        self.switch_to_text_button.grid(row=0, column=2, padx=5, pady=10)

        self.save_button = ctk.CTkButton(button_frame, text="Save CSV", command=lambda: save_csv_content(file_path,
                                                                                                         simpledialog.askstring(
                                                                                                             "Save CSV",
                                                                                                             "Enter a name for the CSV:")))
        self.save_button.grid(row=0, column=3, padx=5, pady=10)

        self.back_button = ctk.CTkButton(button_frame, text="Back",
                                         command=lambda: self.show_text_frame(debits_df, credits_df, df, file_path))
        self.back_button.grid(row=0, column=4, padx=5, pady=10)

        self.plot_frame = ctk.CTkFrame(self.graph_frame)
        self.plot_frame.pack(pady=10, expand=True, fill=ctk.BOTH)

        self.plot_graphs(debits_df, credits_df, plot_type='debits')

    def plot_graphs(self, debits_df, credits_df, plot_type):
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(1, 1, figsize=(16, 8))

        if plot_type == 'credits':
            credit_summary = credits_df.groupby('Category')['Credit'].sum()
            credit_summary.plot(ax=ax, title='Total Credits by Category', kind='bar', color='green', width=0.8)
            ax.set_xlabel('Category')
            ax.set_ylabel('Amount')
            ax.tick_params(axis='x', rotation=90, labelsize=10)
            ax.set_title('Total Credits by Category')

        elif plot_type == 'debits':
            debit_summary = debits_df.groupby('Category')['Debit'].sum()
            debit_summary.plot(ax=ax, title='Total Debits by Category', kind='bar', color='red', width=0.8)
            ax.set_xlabel('Category')
            ax.set_ylabel('Amount')
            ax.tick_params(axis='x', rotation=90, labelsize=10)
            ax.set_title('Total Debits by Category')

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

    def show_saved_csvs(self):
        self.clear_widgets()

        self.saved_csvs_frame = ctk.CTkFrame(self.root)
        self.saved_csvs_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        saved_csvs = load_saved_csvs()
        if saved_csvs:
            for name, path in saved_csvs.items():
                frame = ctk.CTkFrame(self.saved_csvs_frame)
                frame.pack(pady=5, fill='x')

                button = ctk.CTkButton(frame, text=name, command=lambda p=path: self.load_saved_csv(p))
                button.pack(side=ctk.LEFT, padx=5, pady=5)

                delete_button = ctk.CTkButton(frame, text="Delete", command=lambda n=name: self.confirm_delete(n))
                delete_button.pack(side=ctk.RIGHT, padx=5, pady=5)
        else:
            no_csv_label = ctk.CTkLabel(self.saved_csvs_frame, text="No saved CSV files found.")
            no_csv_label.pack(pady=10)

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
            df = pd.read_csv(file_path)
            self.process_csv(df, file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def confirm_exit(self):
        if messagebox.askokcancel("Exit", "Do you really want to exit?"):
            self.root.quit()
