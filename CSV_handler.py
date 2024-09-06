# csv_handler.py

import pandas as pd
from tkinter import messagebox
from Utilises import categorize


def load_csv(self, file_paths):
    """
    Loads and processes multiple CSV files.

    Parameters:
    file_paths (list): List of file paths to CSV files.

    Returns:
    list: A list of tuples where each tuple contains processed DataFrames (debits_df, credits_df, df) and the file path.
    """
    data_frames = []
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path)
            # Call the process_csv method with self
            debits_df, credits_df, processed_df = self.process_csv(df, file_path)
            if processed_df is not None:
                self.df = processed_df  # Assign the processed DataFrame to self.df
                data_frames.append((debits_df, credits_df, processed_df, file_path))
            else:
                messagebox.showerror("Error", "Failed to process CSV file.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file '{file_path}': {e}")
    return data_frames


def process_csv(self, df):
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

    # Assign the processed DataFrame to self.df
    self.df = df

    return debits_df, credits_df, df


