# functionality.py
import pandas as pd

import Utilises
from Utilises import save_csv_content


# functionality.py

def calculate_summary(debits_df, credits_df, excluded_transactions):
    """
    Calculates the summary for debits and credits DataFrames.

    Parameters:
    debits_df (DataFrame): DataFrame containing debit transactions.
    credits_df (DataFrame): DataFrame containing credit transactions.
    excluded_transactions (list): List of excluded transactions.

    Returns:
    dict: A dictionary containing summary data for both debits and credits.
    """
    excluded_set = set(tuple(t) for t in excluded_transactions)
    # Filtered DataFrames
    filtered_debits_df = debits_df[~debits_df.apply(
        lambda row: (row['Started Date'], row['Description'], 'Debit') in excluded_set, axis=1)]
    filtered_credits_df = credits_df[~credits_df.apply(
        lambda row: (row['Started Date'], row['Description'], 'Credit') in excluded_set, axis=1)]

    # Debit summary
    if 'Category' in filtered_debits_df.columns:
        debit_summary = filtered_debits_df.groupby('Category').agg(
            total_spending=('Debit', lambda x: round(abs(x.sum()), 2)),
            min_transaction=('Debit', lambda x: round(x.abs().min(), 2)),
            max_transaction=('Debit', lambda x: round(x.abs().max(), 2)),
            avg_transaction=('Debit', lambda x: round(x.abs().mean(), 2))
        ).reset_index()
    else:
        debit_summary = pd.DataFrame(columns=['Category', 'total_spending', 'min_transaction', 'max_transaction',
                                              'avg_transaction'])

    overall_min_debit = abs(filtered_debits_df['Debit']).min() if not filtered_debits_df.empty else None
    overall_max_debit = abs(filtered_debits_df['Debit']).max() if not filtered_debits_df.empty else None
    total_spent = abs(filtered_debits_df['Debit']).sum() if not filtered_debits_df.empty else 0

    most_expensive_debit_category = (
        debit_summary.loc)[debit_summary['total_spending'].idxmax()] if not debit_summary.empty else None
    least_expensive_debit_category = (
        debit_summary.loc)[debit_summary['total_spending'].idxmin()] if not debit_summary.empty else None

    # Credit summary
    if 'Category' in filtered_credits_df.columns:
        credit_summary = filtered_credits_df.groupby('Category').agg(
            total_income=('Credit', lambda x: round(x.sum(), 2)),
            min_transaction=('Credit', lambda x: round(x.abs().min(), 2)),
            max_transaction=('Credit', lambda x: round(x.abs().max(), 2)),
            avg_transaction=('Credit', lambda x: round(x.abs().mean(), 2))
        ).reset_index()
    else:
        credit_summary = pd.DataFrame(columns=['Category', 'total_income', 'min_transaction', 'max_transaction',
                                               'avg_transaction'])

    overall_min_credit = filtered_credits_df['Credit'].abs().min() if not filtered_credits_df.empty else None
    overall_max_credit = filtered_credits_df['Credit'].abs().max() if not filtered_credits_df.empty else None
    total_made = filtered_credits_df['Credit'].sum() if not filtered_credits_df.empty else 0

    most_profitable_credit_category = (
        credit_summary.loc)[credit_summary['total_income'].idxmax()] if not credit_summary.empty else None
    least_profitable_credit_category = (
        credit_summary.loc)[credit_summary['total_income'].idxmin()] if not credit_summary.empty else None

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


def load_saved_csvs():
    """
    Loads the saved CSV files metadata from a JSON file.

    Returns:
    dict: A dictionary with saved CSV metadata.
    """
    return Utilises.load_saved_csvs()


def delete_saved_csv(name):
    """
    Deletes a saved CSV file and its associated metadata.

    Parameters:
    name (str): The name of the CSV file to delete.
    """
    Utilises.delete_saved_csv(name)


def save_csv(file_path, name, excluded_transactions=None):
    """
    Saves the CSV content to a new file with the option to exclude certain transactions.

    Parameters:
    file_path (str): Path to the original CSV file.
    name (str): The name for the new CSV file.
    excluded_transactions (list): List of excluded transactions.
    """
    save_csv_content(file_path, name, excluded_transactions)
