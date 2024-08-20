import uuid

import customtkinter as ctk
from tkinter import Menu, filedialog, messagebox, simpledialog, ttk, BooleanVar
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Utilises import categorize, save_csv_content, load_saved_csvs, delete_saved_csv, add_keyword_to_category, \
    delete_category, delete_keyword_from_category, open_website, load_category_map


def display_summary(summary_data, summary_frame):
    # Debit Summary Display
    debit_summary_frame = ctk.CTkFrame(summary_frame)
    debit_summary_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    debit_data = summary_data['debits']
    if not debit_data['summary'].empty:
        summary_title = ctk.CTkLabel(debit_summary_frame, text="Debits by Category:",
                                     font=("Helvetica", 30, "bold"))
        summary_title.pack(anchor="center")

        for _, row in debit_data['summary'].iterrows():
            category = row['Category']
            total_spending = row['total_spending']
            min_transaction = row['min_transaction']
            max_transaction = row['max_transaction']
            avg_transaction = row['avg_transaction']

            category_label = ctk.CTkLabel(debit_summary_frame, text=f"{category}:",
                                          font=("Helvetica", 25, "bold"), anchor="center")
            category_label.pack(anchor="center")

            details_label = ctk.CTkLabel(debit_summary_frame,
                                         text=f"Total: {total_spending}, Min: {min_transaction},"
                                              f" Max: {max_transaction},"
                                              f" Avg: {avg_transaction}",
                                         font=("Helvetica", 20), anchor="center")
            details_label.pack(anchor="center")

        overall_label = ctk.CTkLabel(debit_summary_frame,
                                     text=f"Overall Min: {debit_data['overall_min']}"
                                          f" | Overall Max: {debit_data['overall_max']}",
                                     font=("Helvetica", 25, "bold"), anchor="center")
        overall_label.pack(anchor="center")

        expense_label = ctk.CTkLabel(debit_summary_frame,
                                     text=f"Most Expensive Category: {debit_data['most_expensive']['Category']}"
                                          f" ({debit_data['most_expensive']['total_spending']})",
                                     font=("Helvetica", 25, "bold"), anchor="center")
        expense_label.pack(anchor="center")

        expense_label = ctk.CTkLabel(debit_summary_frame,
                                     text=f"Least Expensive Category: {debit_data['least_expensive']['Category']}"
                                          f" ({debit_data['least_expensive']['total_spending']})",
                                     font=("Helvetica", 25, "bold"), anchor="center")
        expense_label.pack(anchor="center")

        total_spent_label = ctk.CTkLabel(debit_summary_frame,
                                         text=f"Total Spent: {debit_data['total_spent']}",
                                         font=("Helvetica", 30, "bold"), anchor="center")
        total_spent_label.pack(anchor="center")

    # Credit Summary Display
    credit_summary_frame = ctk.CTkFrame(summary_frame)
    credit_summary_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

    credit_data = summary_data['credits']
    if not credit_data['summary'].empty:
        summary_title = ctk.CTkLabel(credit_summary_frame, text="Credits by Category:",
                                     font=("Helvetica", 30, "bold"))
        summary_title.pack(anchor="center")

        for _, row in credit_data['summary'].iterrows():
            category = row['Category']
            total_income = row['total_income']
            min_transaction = row['min_transaction']
            max_transaction = row['max_transaction']
            avg_transaction = row['avg_transaction']

            category_label = ctk.CTkLabel(credit_summary_frame, text=f"{category}:",
                                          font=("Helvetica", 25, "bold"), anchor="center")
            category_label.pack(anchor="center")

            details_label = ctk.CTkLabel(credit_summary_frame,
                                         text=f"Total: {total_income}, Min: {min_transaction}, Max: {max_transaction},"
                                              f" Avg: {avg_transaction}",
                                         font=("Helvetica", 20), anchor="center")
            details_label.pack(anchor="center")

        overall_label = ctk.CTkLabel(credit_summary_frame,
                                     text=f"Overall Min: {credit_data['overall_min']}"
                                          f" | Overall Max: {credit_data['overall_max']}",
                                     font=("Helvetica", 25, "bold"), anchor="center")
        overall_label.pack(anchor="center")

        profit_label = ctk.CTkLabel(credit_summary_frame,
                                    text=f"Most Profitable Category: {credit_data['most_profitable']['Category']}"
                                         f" ({credit_data['most_profitable']['total_income']})",
                                    font=("Helvetica", 25, "bold"), anchor="center")
        profit_label.pack(anchor="center")

        profit_label = ctk.CTkLabel(credit_summary_frame,
                                    text=f"Least Profitable Category: {credit_data['least_profitable']['Category']}"
                                         f" ({credit_data['least_profitable']['total_income']})",
                                    font=("Helvetica", 25, "bold"), anchor="center")
        profit_label.pack(anchor="center")

        total_made_label = ctk.CTkLabel(credit_summary_frame,
                                        text=f"Total Made: {credit_data['total_made']}",
                                        font=("Helvetica", 30, "bold"), anchor="center")
        total_made_label.pack(anchor="center")


class CSVViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.attributes('-fullscreen', True)
        self.root.iconbitmap('favicon.ico')
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.create_widgets()
        self.excluded_transactions = []  # To track excluded transactions
        self.df = None  # Initialize self.df

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
        self.exit_button.grid(row=4, column=0, padx=20, pady=10)

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
            df['Debit'] = df.apply(lambda row: row['Amount'] if row['Amount'] < 0 else None, axis=1)
            df['Credit'] = df.apply(lambda row: row['Amount'] if row['Amount'] > 0 else None, axis=1)
            df['Category'] = df.apply(lambda row: categorize(row['Description']), axis=1)

            debits_df = df[df['Debit'].notna()].copy()
            credits_df = df[df['Credit'].notna()].copy()

        elif 'Debit Amount' in df.columns and 'Credit Amount' in df.columns:
            required_columns = ['Posted Transactions Date', 'Description1', 'Debit Amount', 'Credit Amount', 'Balance']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = '' if col not in ['Debit Amount', 'Credit Amount'] else 0
            df = df.loc[:, required_columns]
            df['Debit'] = df['Debit Amount']
            df['Credit'] = df['Credit Amount']
            df['Category'] = df.apply(lambda row: categorize(row['Description1']), axis=1)
            df.rename(columns={'Posted Transactions Date': 'Started Date', 'Description1': 'Description'}, inplace=True)

            debits_df = df[(df['Debit'].notna()) & (df['Credit'].isna())].copy()
            credits_df = df[(df['Credit'].notna()) & (df['Debit'].isna())].copy()

        elif 'Debit' in df.columns and 'Credit' in df.columns:
            required_columns = ['Date', 'Details', 'Debit', 'Credit', 'Balance']
            for col in required_columns:
                if col not in df.columns:
                    df[col] = '' if col not in ['Debit', 'Credit', 'Balance'] else 0
            df = df.loc[:, required_columns]
            df['Category'] = df.apply(lambda row: categorize(row['Details']), axis=1)
            df.rename(columns={'Date': 'Started Date', 'Details': 'Description'}, inplace=True)

            debits_df = df[(df['Debit'].notna()) & (df['Credit'].isna())].copy()
            credits_df = df[(df['Credit'].notna()) & (df['Debit'].isna())].copy()

        else:
            messagebox.showerror("Error",
                                 "CSV file must contain 'Amount' column or both 'Debit Amount' and 'Credit Amount' "
                                 "columns.")
            return

        self.df = df
        self.show_text_frame(debits_df, credits_df, df, file_path)

    def calculate_summary(self, debits_df, credits_df):
        # Filter out excluded transactions
        excluded_set = set(tuple(t) for t in self.excluded_transactions)

        filtered_debits_df = debits_df[~debits_df.apply(
            lambda row: (row['Started Date'], row['Description'], 'Debit') in excluded_set, axis=1)]
        filtered_credits_df = credits_df[~credits_df.apply(
            lambda row: (row['Started Date'], row['Description'], 'Credit') in excluded_set, axis=1)]

        # Debit summary calculation with absolute values
        debit_summary = filtered_debits_df.groupby('Category').agg(
            total_spending=('Debit', lambda x: round(abs(x.sum()), 2)),
            min_transaction=('Debit', lambda x: round(x.abs().min(), 2)),
            max_transaction=('Debit', lambda x: round(x.abs().max(), 2)),
            avg_transaction=('Debit', lambda x: round(x.abs().mean(), 2))
        ).reset_index()

        overall_min_debit = abs(filtered_debits_df['Debit']).min() if not filtered_debits_df.empty else None
        overall_max_debit = abs(filtered_debits_df['Debit']).max() if not filtered_debits_df.empty else None
        total_spent = abs(filtered_debits_df['Debit']).sum() if not filtered_debits_df.empty else 0

        if not debit_summary.empty:
            debit_summary['Absolute Debit'] = debit_summary['total_spending']
            most_expensive_debit_category = debit_summary.loc[debit_summary['Absolute Debit'].idxmax()]
            least_expensive_debit_category = debit_summary.loc[debit_summary['Absolute Debit'].idxmin()]
        else:
            most_expensive_debit_category = None
            least_expensive_debit_category = None

        # Credit summary calculation with absolute values
        credit_summary = filtered_credits_df.groupby('Category').agg(
            total_income=('Credit', lambda x: round(x.sum(), 2)),
            min_transaction=('Credit', lambda x: round(x.abs().min(), 2)),
            max_transaction=('Credit', lambda x: round(x.abs().max(), 2)),
            avg_transaction=('Credit', lambda x: round(x.abs().mean(), 2))
        ).reset_index()

        overall_min_credit = filtered_credits_df['Credit'].abs().min() if not filtered_credits_df.empty else None
        overall_max_credit = filtered_credits_df['Credit'].abs().max() if not filtered_credits_df.empty else None
        total_made = filtered_credits_df['Credit'].sum() if not filtered_credits_df.empty else 0

        if not credit_summary.empty:
            most_profitable_credit_category = credit_summary.loc[credit_summary['total_income'].idxmax()]
            least_profitable_credit_category = credit_summary.loc[credit_summary['total_income'].idxmin()]
        else:
            most_profitable_credit_category = None
            least_profitable_credit_category = None

        return {
            'debits': {
                'summary': debit_summary,
                'overall_min': overall_min_debit,
                'overall_max': overall_max_debit,
                'total_spent': total_spent,
                'most_expensive': most_expensive_debit_category,
                'least_expensive': least_expensive_debit_category
            },
            'credits': {
                'summary': credit_summary,
                'overall_min': overall_min_credit,
                'overall_max': overall_max_credit,
                'total_made': total_made,
                'most_profitable': most_profitable_credit_category,
                'least_profitable': least_profitable_credit_category
            }
        }

    def show_spending_summary(self, debits_df, credits_df):
        self.clear_widgets()

        summary_frame = ctk.CTkFrame(self.root)
        summary_frame.pack(padx=20, pady=20, expand=True, fill=ctk.BOTH)

        # Title
        title_label = ctk.CTkLabel(summary_frame, text="Spending & Income Summary",
                                   font=("Helvetica", 40, "bold"), anchor="center")
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Calculate the summary
        summary_data = self.calculate_summary(debits_df, credits_df)

        # Display the summary
        display_summary(summary_data, summary_frame)

        # Buttons
        button_frame = ctk.CTkFrame(summary_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        self.back_button = ctk.CTkButton(button_frame, text="Back", font=("Helvetica", 18),
                                         command=lambda: self.show_text_frame(debits_df, credits_df, self.df, ""))
        self.back_button.pack(pady=10, side=ctk.LEFT)

        # Make sure both columns expand equally to fill the screen
        summary_frame.grid_columnconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(1, weight=1)

        # Make sure the row with the frames expands to fill the available vertical space
        summary_frame.grid_rowconfigure(1, weight=1)

    def show_text_frame(self, debits_df, credits_df, df, file_path):
        self.clear_widgets()

        self.table_frame = ctk.CTkFrame(self.root)
        self.table_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        notebook = ttk.Notebook(self.table_frame)
        notebook.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        debits_copy = debits_df.copy()
        credits_copy = credits_df.copy()

        debits_frame = ttk.Frame(notebook)
        credits_frame = ttk.Frame(notebook)

        notebook.add(debits_frame, text="Debits")
        notebook.add(credits_frame, text="Credits")

        self.create_table(debits_frame, debits_copy, "Debits")
        self.create_table(credits_frame, credits_copy, "Credits")

        self.update_totals_frame()

        self.switch_to_graph_button = ctk.CTkButton(self.table_frame, text="Show Graphs",
                                                    command=lambda: self.show_graph_frame(debits_df, credits_df, df,
                                                                                          file_path))
        self.switch_to_graph_button.pack(pady=10)

        self.show_summary_button = ctk.CTkButton(self.table_frame, text="Show Spending Summary",
                                                 command=lambda: self.show_spending_summary(debits_df, credits_df))
        self.show_summary_button.pack(pady=10)

        self.save_button = ctk.CTkButton(self.table_frame, text="Save CSV", command=lambda: save_csv_content(
            file_path, simpledialog.askstring("Save CSV", "Enter a name for the CSV:"),
            excluded_transactions=self.excluded_transactions))
        self.save_button.pack(pady=10)

        self.back_button = ctk.CTkButton(self.table_frame, text="Back", command=self.handle_back)
        self.back_button.pack(pady=10)

    def handle_back(self):
        self.reset_excluded_transactions()
        self.create_widgets()

    def reset_excluded_transactions(self):
        self.excluded_transactions = []

    def create_table(self, parent_frame, dataframe, table_type):
        """Create a table for displaying transactions with inclusion/exclusion checkboxes."""
        columns = list(dataframe.columns)
        columns.append("Include")

        tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        tree.pack(expand=True, fill=ctk.BOTH)

        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure()
        scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        if table_type == "Debits":
            self.debits_check_vars = {}
            self.debits_tree_rows = {}
            self.debits_tree = tree  # Save the reference to the debits TreeView
        else:
            self.credits_check_vars = {}
            self.credits_tree_rows = {}
            self.credits_tree = tree  # Save the reference to the credits TreeView

        for index, row in dataframe.iterrows():
            include_var = BooleanVar()

            values = tuple(row[col] for col in columns[:-1])

            unique_id = f"{table_type}_{uuid.uuid4()}"
            item_id = tree.insert("", "end", iid=unique_id, values=values)

            if table_type == "Debits":
                self.debits_tree_rows[unique_id] = row
                self.debits_check_vars[unique_id] = include_var
            else:
                self.credits_tree_rows[unique_id] = row
                self.credits_check_vars[unique_id] = include_var

            transaction_type = 'Debit' if table_type == "Debits" else 'Credit'
            transaction = (row['Started Date'], row['Description'], transaction_type)

            # Set initial state based on excluded_transactions
            include_var.set(transaction not in self.excluded_transactions)
            tree.set(item_id, "Include", "Included" if include_var.get() else "Excluded")

        # Ensure that the tree is updated whenever the view is created
        self.sync_tree_with_state(tree, table_type)
        tree.bind("<ButtonRelease-1>", lambda event: self.toggle_checkbox(tree, event, table_type))

    def toggle_checkbox(self, tree, event, table_type):
        """Handle checkbox toggling for excluding/including transactions."""
        item_id = tree.identify_row(event.y)
        column = tree.identify_column(event.x)
        include_column_index = f"#{len(tree['columns'])}"

        if column == include_column_index:
            include_var = None
            row = None

            if table_type == "Debits" and item_id in self.debits_check_vars:
                include_var = self.debits_check_vars[item_id]
                row = self.debits_tree_rows[item_id]
            elif table_type == "Credits" and item_id in self.credits_check_vars:
                include_var = self.credits_check_vars[item_id]
                row = self.credits_tree_rows[item_id]

            if include_var is not None and row is not None:
                current_state = include_var.get()
                include_var.set(not current_state)
                new_text = "Included" if include_var.get() else "Excluded"
                tree.set(item_id, "Include", new_text)

                self.toggle_transaction(row, include_var)

                self.sync_tree_with_state(tree, table_type)

    def toggle_transaction(self, row, include_var):
        transaction_type = 'Debit' if pd.notna(row['Debit']) and pd.isna(row['Credit']) else 'Credit'
        transaction = (row['Started Date'], row['Description'], transaction_type)
        if include_var.get():
            if transaction in self.excluded_transactions:
                self.excluded_transactions.remove(transaction)
        else:
            if transaction not in self.excluded_transactions:
                self.excluded_transactions.append(transaction)

        self.update_totals_frame()

    def sync_tree_with_state(self, tree, table_type):
        check_vars = self.debits_check_vars if table_type == "Debits" else self.credits_check_vars
        tree_rows = self.debits_tree_rows if table_type == "Debits" else self.credits_tree_rows
        for item_id, include_var in check_vars.items():
            row = tree_rows[item_id]

            transaction_type = 'Debit' if pd.notna(row['Debit']) and pd.isna(row['Credit']) else 'Credit'
            transaction = (row['Started Date'], row['Description'], transaction_type)

            include_var.set(transaction not in self.excluded_transactions)
            tree.set(item_id, "Include", "Included" if include_var.get() else "Excluded")

        self.update_totals_frame()

    def update_totals_frame(self):
        if self.df is None:
            return

        # Ensure correct filtering of both debits and credits
        remaining_df = self.df[~self.df.apply(lambda row: (row['Started Date'], row['Description'],
                                                           'Debit' if pd.notna(row['Debit']) and pd.isna(row['Credit'])
                                                           else 'Credit') in self.excluded_transactions, axis=1)]

        if not remaining_df.empty:
            total_debits = remaining_df['Debit'].sum()
            total_credits = remaining_df['Credit'].sum()
            ending_balance = remaining_df['Balance'].iloc[-1] if 'Balance' in remaining_df.columns else 0
        else:
            total_debits = 0
            total_credits = 0
            ending_balance = 0

        if hasattr(self, 'totals_frame'):
            self.totals_frame.destroy()

        self.totals_frame = ctk.CTkFrame(self.table_frame)
        self.totals_frame.pack(padx=10, pady=10, fill=ctk.X)

        totals_label = ctk.CTkLabel(self.totals_frame, text=f"Total Debits: {total_debits}   |   "
                                                            f"Total Credits: {total_credits}   |   "
                                                            f"Ending Balance: {ending_balance}",
                                    font=("Helvetica", 16, "bold"))
        totals_label.pack(pady=10)

    def show_graph_frame(self, debits_df, credits_df, df, file_path):
        """Display the graph view and synchronize the table with the current exclusion state."""
        self.clear_widgets()

        # Create a set of excluded transactions using tuples
        excluded_set = set(tuple(t) for t in self.excluded_transactions)

        # Use copies of the DataFrames to preserve original data
        remaining_debits_df = debits_df.copy()
        remaining_credits_df = credits_df.copy()

        # Filter out excluded transactions from debits and credits
        remaining_debits_df = remaining_debits_df[~remaining_debits_df.apply(
            lambda row: (row['Started Date'], row['Description'], 'Debit') in excluded_set, axis=1)]
        remaining_credits_df = remaining_credits_df[~remaining_credits_df.apply(
            lambda row: (row['Started Date'], row['Description'], 'Credit') in excluded_set, axis=1)]

        self.graph_frame = ctk.CTkFrame(self.root)
        self.graph_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        button_frame = ctk.CTkFrame(self.graph_frame)
        button_frame.pack(pady=10)

        self.debits_button = ctk.CTkButton(button_frame, text="Show Debits Graph",
                                           command=lambda: self.plot_graphs(remaining_debits_df, remaining_credits_df,
                                                                            plot_type='debits'))
        self.debits_button.grid(row=0, column=0, padx=5, pady=10)

        self.credits_button = ctk.CTkButton(button_frame, text="Show Credits Graph",
                                            command=lambda: self.plot_graphs(remaining_debits_df, remaining_credits_df,
                                                                             plot_type='credits'))
        self.credits_button.grid(row=0, column=1, padx=5, pady=10)

        self.back_button = ctk.CTkButton(button_frame, text="Back",
                                         command=lambda: self.show_text_frame(debits_df, credits_df, df, file_path))
        self.back_button.grid(row=0, column=2, padx=5, pady=10)

        self.plot_frame = ctk.CTkFrame(self.graph_frame)
        self.plot_frame.pack(pady=10, expand=True, fill=ctk.BOTH)

        self.plot_graphs(remaining_debits_df, remaining_credits_df, plot_type='debits')

        self.graph_frame.update_idletasks()

    # Ensure plot_graphs function now uses the passed filtered DataFrames
    def plot_graphs(self, debits_df, credits_df, plot_type):
        """Plot the graphs using the filtered DataFrames."""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(1, 1, figsize=(16, 8))

        if plot_type == 'credits':
            if credits_df.empty:
                ax.text(0.5, 0.5, 'No Credits to Display', horizontalalignment='center', verticalalignment='center')
            else:
                credit_summary = credits_df.groupby('Category')['Credit'].sum()
                credit_summary.plot(ax=ax, title='Total Credits by Category', kind='bar', color='green', width=0.8)
                ax.set_xlabel('Category')
                ax.set_ylabel('Amount')
                ax.tick_params(axis='x', rotation=90, labelsize=10)
                ax.set_title('Total Credits by Category')

        elif plot_type == 'debits':
            if debits_df.empty:
                ax.text(0.5, 0.5, 'No Debits to Display', horizontalalignment='center', verticalalignment='center')
            else:
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

        self.title_label = ctk.CTkLabel(self.root, text="Select a saved CSV file",
                                        font=("Helvetica", 30, "bold"))
        self.title_label.pack(pady=10)  # Ensure this line is not missing or commented out.

        self.saved_csvs_frame = ctk.CTkFrame(self.root)
        self.saved_csvs_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        saved_csvs = load_saved_csvs()
        if saved_csvs:
            for name, info in saved_csvs.items():
                frame = ctk.CTkFrame(self.saved_csvs_frame)
                frame.pack(pady=5, fill='x')

                button = ctk.CTkButton(frame, text=name, command=lambda n=name: self.load_saved_csv(n))
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

    def load_saved_csv(self, name):
        try:
            saved_csvs = load_saved_csvs()
            if name in saved_csvs:
                file_info = saved_csvs[name]
                file_path = file_info['file_path']
                self.excluded_transactions = [tuple(item) for item in file_info.get('excluded_transactions', [])]

                df = pd.read_csv(file_path)
                self.process_csv(df, file_path)

                self.sync_tree_with_state(self.debits_tree, "Debits")
                self.sync_tree_with_state(self.credits_tree, "Credits")
            else:
                messagebox.showerror("Error", f"CSV file '{name}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def confirm_exit(self):
        if messagebox.askokcancel("Exit", "Do you really want to exit?"):
            self.root.quit()
