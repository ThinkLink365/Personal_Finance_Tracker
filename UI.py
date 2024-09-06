# ui.py

import uuid
from tkinter import filedialog, messagebox, simpledialog, ttk, BooleanVar

import customtkinter as ctk
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from CSV_handler import process_csv
from Utilises import open_website
from categories import manage_categories
from functionality import calculate_summary, load_saved_csvs, delete_saved_csv, save_csv
from compare import execute_csv_comparison, create_comparison_results, create_comparison_summary, \
    initiate_csv_selection, append_csv_for_comparison, retrieve_csv_data


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


def display_summary_statistics(frame, summary_data, file_label, is_credit=False):
    """
    Helper function to display the summary statistics for debits or credits in a given frame.

    Parameters:
    frame (CTkFrame): The frame where the summary statistics should be displayed.
    summary_data (dict): The summary data to display.
    file_label (str): The label to indicate which file the data belongs to.
    is_credit (bool): Whether the data being displayed is for credits or debits.
    """
    total_text = "Total Earned" if is_credit else "Total Spent"
    min_text = "Smallest Transaction"
    max_text = "Biggest Transaction"
    most_expensive_text = "Most Profitable Category" if is_credit else "Most Expensive Category"
    least_expensive_text = "Least Profitable Category" if is_credit else "Least Expensive Category"

    total_label = ctk.CTkLabel(
        frame,
        text=(
            f"{total_text} ({file_label}): "
            f"{summary_data.get('total_spent', 'N/A') if not is_credit else summary_data.get('total_made', 'N/A')}"
        ),
        font=("Helvetica", 20)
    )

    total_label.pack(anchor="w", padx=10, pady=5)

    min_label = ctk.CTkLabel(frame,
                             text=f"{min_text} ({file_label}): {summary_data.get('overall_min', 'N/A')}",
                             font=("Helvetica", 20))
    min_label.pack(anchor="w", padx=10, pady=5)

    max_label = ctk.CTkLabel(frame,
                             text=f"{max_text} ({file_label}): {summary_data.get('overall_max', 'N/A')}",
                             font=("Helvetica", 20))
    max_label.pack(anchor="w", padx=10, pady=5)

    # Safely get most_expensive and least_expensive categories
    most_expensive_category = summary_data.get('most_expensive') if not is_credit else summary_data.get(
        'most_profitable')
    if most_expensive_category is not None and not most_expensive_category.empty:
        most_expensive_category_name = most_expensive_category.get('Category', 'N/A')
        most_expensive_total = most_expensive_category.get('total_spending',
                                                           'N/A') if not is_credit else most_expensive_category.get(
            'total_earnings', 'N/A')
    else:
        most_expensive_category_name = 'N/A'
        most_expensive_total = 'N/A'

    most_expensive_label = ctk.CTkLabel(frame,
                                        text=f"{most_expensive_text} ({file_label}): {most_expensive_category_name} - "
                                             f"{most_expensive_total}",
                                        font=("Helvetica", 20))
    most_expensive_label.pack(anchor="w", padx=10, pady=5)

    least_expensive_category = summary_data.get('least_expensive') if not is_credit else summary_data.get(
        'least_profitable')
    if least_expensive_category is not None and not least_expensive_category.empty:
        least_expensive_category_name = least_expensive_category.get('Category', 'N/A')
        least_expensive_total = least_expensive_category.get('total_spending',
                                                             'N/A') if not is_credit else least_expensive_category.get(
            'total_earnings', 'N/A')
    else:
        least_expensive_category_name = 'N/A'
        least_expensive_total = 'N/A'

    least_expensive_label = ctk.CTkLabel(frame,
                                         text=f"{least_expensive_text} ({file_label}): {least_expensive_category_name}"
                                              f" - {least_expensive_total}",
                                         font=("Helvetica", 20))
    least_expensive_label.pack(anchor="w", padx=10, pady=5)


class CSVViewerApp:
    def __init__(self, root):

        self.credits_df = None
        self.debits_df = None
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.attributes('-fullscreen', True)
        self.root.iconbitmap('favicon.ico')
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.excluded_transactions = []
        self.selected_csvs = []
        self.df = None
        self.debits_tree = None
        self.credits_tree = None
        self.create_widgets()

    def create_widgets(self):
        """
        Creates the initial UI widgets, including the menu and buttons.
        """
        self.clear_widgets()

        self.title_label = ctk.CTkLabel(self.root, text="Welcome to the Personal Finance Tracker",
                                        font=("Helvetica", 30, "bold"))
        self.title_label.pack(pady=10)

        self.subtitle_label = ctk.CTkLabel(self.root, text="Please select CSV files to be loaded",
                                           font=("Helvetica", 20, "bold"))
        self.subtitle_label.pack(pady=10)

        self.button_frame = ctk.CTkFrame(self.root)
        self.button_frame.pack(pady=10)

        self.load_button = ctk.CTkButton(self.button_frame, text="Load CSVs", command=self.load_csv)
        self.load_button.grid(row=0, column=0, padx=20, pady=10)

        self.saved_csvs_button = ctk.CTkButton(self.button_frame, text="Saved CSVs", command=self.show_saved_csvs)
        self.saved_csvs_button.grid(row=1, column=0, padx=20, pady=10)

        self.manage_categories_button = ctk.CTkButton(self.button_frame, text="Manage Categories",
                                                      command=self.manage_categories)
        self.manage_categories_button.grid(row=2, column=0, padx=20, pady=10)

        self.compare_csvs_button = ctk.CTkButton(self.button_frame, text="Compare CSVs",
                                                 command=self.select_csvs_for_comparison)
        self.compare_csvs_button.grid(row=3, column=0, padx=20, pady=10)

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
        """
        Clears all widgets from the root window.
        """
        for widget in self.root.winfo_children():
            widget.destroy()

    def load_csv(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("CSV files", "*.csv")])
        if file_paths:
            for file_path in file_paths:
                try:
                    df = pd.read_csv(file_path)
                    debits_df, credits_df, processed_df = process_csv(self, df)
                    if processed_df is not None:
                        self.df = processed_df  # Ensure self.df is set
                        self.show_text_frame(debits_df, credits_df, self.df, file_path)
                        self.update_totals_frame()  # Call after self.df is set
                    else:
                        messagebox.showerror("Error", "Failed to process CSV file.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load CSV file '{file_path}': {e}")

    def show_text_frame(self, debits_df, credits_df, df, file_path):
        """
        Displays the main text frame with debits and credits data side by side.

        Parameters:
        debits_df (DataFrame): DataFrame containing debit transactions.
        credits_df (DataFrame): DataFrame containing credit transactions.
        df (DataFrame): The original DataFrame.
        file_path (str): The path to the CSV file.
        """
        self.clear_widgets()

        self.table_frame = ctk.CTkFrame(self.root)
        self.table_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        notebook = ttk.Notebook(self.table_frame)
        notebook.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        debits_frame = ttk.Frame(notebook)
        credits_frame = ttk.Frame(notebook)

        notebook.add(debits_frame, text="Debits")
        notebook.add(credits_frame, text="Credits")

        self.create_table(debits_frame, debits_df, "Debits")
        self.create_table(credits_frame, credits_df, "Credits")

        self.switch_to_graph_button = ctk.CTkButton(self.table_frame, text="Show Graphs",
                                                    command=lambda: self.show_graph_frame(debits_df, credits_df, df,
                                                                                          file_path))
        self.switch_to_graph_button.pack(pady=10)

        self.show_summary_button = ctk.CTkButton(self.table_frame, text="Show Spending Summary",
                                                 command=lambda: self.show_spending_summary(debits_df, credits_df))
        self.show_summary_button.pack(pady=10)

        self.save_button = ctk.CTkButton(self.table_frame, text="Save CSV",
                                         command=lambda: save_csv(file_path,
                                                                  simpledialog.askstring("Save CSV",
                                                                                         "Enter a name for the CSV:"),
                                                                  excluded_transactions=self.excluded_transactions))
        self.save_button.pack(pady=10)

        self.back_button = ctk.CTkButton(self.table_frame, text="Back", command=self.create_widgets)
        self.back_button.pack(pady=10)

        self.update_totals_frame()

    def create_table(self, parent_frame, dataframe, table_type):
        """
        Creates a table for displaying transactions with inclusion/exclusion checkboxes.

        Parameters:
        parent_frame (Frame): The parent frame to contain the table.
        dataframe (DataFrame): The DataFrame containing the transaction data.
        table_type (str): Indicates whether the table is for 'Debits' or 'Credits'.
        """
        columns = list(dataframe.columns)
        columns.append("Include")

        tree = ttk.Treeview(parent_frame, columns=columns, show='headings')
        tree.pack(expand=True, fill=ctk.BOTH)

        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center")

        if table_type == "Debits":
            self.debits_tree = tree
            self.debits_check_vars = {}
            self.debits_tree_rows = {}
        else:
            self.credits_tree = tree
            self.credits_check_vars = {}
            self.credits_tree_rows = {}

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

            include_var.set(transaction not in self.excluded_transactions)
            tree.set(item_id, "Include", "Included" if include_var.get() else "Excluded")

        tree.bind("<ButtonRelease-1>", lambda event: self.toggle_checkbox(tree, event, table_type))

    def toggle_checkbox(self, tree, event, table_type):
        """
        Toggles the checkbox for including or excluding a transaction.

        Parameters:
        tree (ttk.Treeview): The tree view widget.
        event: The event object from the tree view.
        table_type (str): Indicates whether the table is for 'Debits' or 'Credits'.
        """
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
        """
        Toggles the inclusion or exclusion of a transaction based on the checkbox state.

        Parameters:
        row (Series): The row of the DataFrame corresponding to the transaction.
        include_var (BooleanVar): The variable controlling the inclusion/exclusion state.
        """
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
        """
        Synchronizes the state of the UI tree view with the current transaction data.

        Parameters:
        tree (ttk.Treeview): The tree view widget to synchronize.
        table_type (str): The type of data ('Debits' or 'Credits') being handled.
        """
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
        """
        Updates the totals frame with the current totals for debits, credits, and the ending balance.
        """
        if self.df is None:
            return

        remaining_df = self.df[~self.df.apply(lambda row: (
                                                              row['Started Date'], row['Description'],
                                                              'Debit' if pd.notna(row['Debit']) and pd.isna(
                                                                  row['Credit']) else 'Credit'
                                                          ) in self.excluded_transactions, axis=1)]

        total_debits = remaining_df['Debit'].sum() if not remaining_df.empty else 0
        total_credits = remaining_df['Credit'].sum() if not remaining_df.empty else 0
        ending_balance = remaining_df['Balance'].iloc[
            -1] if not remaining_df.empty and 'Balance' in remaining_df.columns else 0

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
        """
        Displays the graph view and synchronizes the table with the current exclusion state.

        Parameters:
        debits_df (DataFrame): DataFrame containing debit transactions.
        credits_df (DataFrame): DataFrame containing credit transactions.
        df (DataFrame): The original DataFrame.
        file_path (str): The path to the CSV file.
        """
        self.clear_widgets()

        excluded_set = set(tuple(t) for t in self.excluded_transactions)

        remaining_debits_df = debits_df[~debits_df.apply(
            lambda row: (row['Started Date'], row['Description'], 'Debit') in excluded_set, axis=1)]
        remaining_credits_df = credits_df[~credits_df.apply(
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

    def plot_graphs(self, debits_df, credits_df, plot_type):
        """
        Plots the graphs using the filtered DataFrames.

        Parameters:
        debits_df (DataFrame): DataFrame containing debit transactions.
        credits_df (DataFrame): DataFrame containing credit transactions.
        plot_type (str): The type of plot ('debits' or 'credits').
        """
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
        """
        Displays a list of saved CSVs for the user to select and load.
        """
        self.clear_widgets()

        self.title_label = ctk.CTkLabel(self.root, text="Select a saved CSV file",
                                        font=("Helvetica", 30, "bold"))
        self.title_label.pack(pady=10)

        # Create a scrollable frame to hold the list of saved CSVs
        scrollable_frame = ctk.CTkScrollableFrame(self.root)
        scrollable_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

        saved_csvs = load_saved_csvs()
        if saved_csvs:
            for name, info in saved_csvs.items():
                frame = ctk.CTkFrame(scrollable_frame)
                frame.pack(pady=5, fill='x')

                button = ctk.CTkButton(frame, text=name, command=lambda n=name: self.load_saved_csv(n))
                button.pack(side=ctk.LEFT, padx=5, pady=5)

                delete_button = ctk.CTkButton(frame, text="Delete", command=lambda n=name: self.confirm_delete(n))
                delete_button.pack(side=ctk.RIGHT, padx=5, pady=5)
        else:
            no_csv_label = ctk.CTkLabel(scrollable_frame, text="No saved CSV files found.")
            no_csv_label.pack(pady=10)

        self.back_button = ctk.CTkButton(self.root, text="Back", command=self.create_widgets)
        self.back_button.pack(pady=10)

    def confirm_delete(self, name):
        """
        Confirms the deletion of a saved CSV file.

        Parameters:
        name (str): The name of the CSV file to delete.
        """
        if messagebox.askokcancel("Delete", f"Do you really want to delete '{name}'?"):
            self.delete_csv(name)

    def delete_csv(self, name):
        """
        Deletes a saved CSV file and refreshes the saved CSVs view.

        Parameters:
        name (str): The name of the CSV file to delete.
        """
        delete_saved_csv(name)
        self.show_saved_csvs()

    def load_saved_csv(self, name):
        """
        Loads a saved CSV file, restores excluded transactions, and synchronizes the UI with the data.

        Parameters:
        name (str): The name of the saved CSV file to load.
        """
        try:
            saved_csvs = load_saved_csvs()
            if name in saved_csvs:
                file_info = saved_csvs[name]
                file_path = file_info['file_path']
                self.excluded_transactions = [tuple(item) for item in file_info.get('excluded_transactions', [])]

                df = pd.read_csv(file_path)
                debits_df, credits_df, _ = process_csv(self, df)

                self.show_text_frame(debits_df, credits_df, df, file_path)
            else:
                messagebox.showerror("Error", f"CSV file '{name}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file: {e}")

    def confirm_exit(self):
        """
        Confirms if the user wants to exit the application.
        """
        if messagebox.askokcancel("Exit", "Do you really want to exit?"):
            self.root.quit()

    def manage_categories(self):
        """
        Opens the category management interface.
        """
        manage_categories(self, self.create_widgets)

    def select_csvs_for_comparison(self):
        initiate_csv_selection(self.root, self.clear_widgets, self.add_csv_to_compare, self.create_widgets,
                               self.confirm_delete)

    def add_csv_to_compare(self, name):
        append_csv_for_comparison(self, name, self.selected_csvs, retrieve_csv_data, self.run_csv_comparison,
                                  process_csv,
                                  load_saved_csvs)

    def run_csv_comparison(self, selected_csvs):
        results, file_name1, file_name2 = execute_csv_comparison(selected_csvs)
        self.show_comparison_results(results, file_name1, file_name2)

    def show_comparison_results(self, results, file_name1, file_name2):
        create_comparison_results(self.root, self.clear_widgets, results, file_name1, file_name2, self.create_widgets,
                                  self.show_comparison_summary)

    def show_comparison_summary(self, results, file_name1, file_name2):

        create_comparison_summary(self.root, self.clear_widgets, results, file_name1, file_name2, self.create_widgets)

    def show_spending_summary(self, debits_df, credits_df):
        """
        Displays a summary of spending and income based on the processed data.

        Parameters:
        debits_df (DataFrame): DataFrame containing debit transactions.
        credits_df (DataFrame): DataFrame containing credit transactions.
        """
        self.clear_widgets()

        summary_frame = ctk.CTkFrame(self.root)
        summary_frame.pack(padx=20, pady=20, expand=True, fill=ctk.BOTH)

        title_label = ctk.CTkLabel(summary_frame, text="Spending & Income Summary",
                                   font=("Helvetica", 40, "bold"), anchor="center")
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Pass excluded transactions to the summary calculation function
        summary_data = calculate_summary(debits_df, credits_df, self.excluded_transactions)

        # Display the summary
        display_summary(summary_data, summary_frame)

        button_frame = ctk.CTkFrame(summary_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        self.back_button = ctk.CTkButton(button_frame, text="Back", font=("Helvetica", 18),
                                         command=lambda: self.show_text_frame(debits_df, credits_df, self.df, ""))
        self.back_button.pack(pady=10, side=ctk.LEFT)

        summary_frame.grid_columnconfigure(0, weight=1)
        summary_frame.grid_columnconfigure(1, weight=1)
        summary_frame.grid_rowconfigure(1, weight=1)
