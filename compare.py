# compare.py

import os
import pandas as pd
import customtkinter as ctk
from tkinter import messagebox
from CSV_handler import process_csv
from functionality import load_saved_csvs


def initiate_csv_selection(root, clear_widgets, add_csv_to_compare, create_widgets, confirm_delete):
    """
    Displays a list of saved CSVs for the user to select and compare.
    """
    clear_widgets()

    title_label = ctk.CTkLabel(root, text="Select two CSV files to compare",
                               font=("Helvetica", 30, "bold"))
    title_label.pack(pady=10)

    scrollable_frame = ctk.CTkScrollableFrame(root)
    scrollable_frame.pack(padx=10, pady=10, expand=True, fill=ctk.BOTH)

    saved_csvs = load_saved_csvs()

    if saved_csvs:
        for name, info in saved_csvs.items():
            frame = ctk.CTkFrame(scrollable_frame)
            frame.pack(pady=5, fill='x')

            button = ctk.CTkButton(frame, text=name, command=lambda n=name: add_csv_to_compare(n))
            button.pack(side=ctk.LEFT, padx=5, pady=5)

            delete_button = ctk.CTkButton(frame, text="Delete", command=lambda n=name: confirm_delete(n))
            delete_button.pack(side=ctk.RIGHT, padx=5, pady=5)
    else:
        no_csv_label = ctk.CTkLabel(scrollable_frame, text="No saved CSV files found.")
        no_csv_label.pack(pady=10)

    back_button = ctk.CTkButton(root, text="Back", command=create_widgets)
    back_button.pack(pady=10)


def retrieve_csv_data(self, name, load_saved_csvs, process_csv):
    """
    Loads a saved CSV file and returns the data without processing.

    Parameters:
    name (str): The name of the saved CSV file to load.
    load_saved_csvs (func): Function to load saved CSVs.
    process_csv (func): Method to process a loaded CSV file.

    Returns:
    tuple: A tuple containing (debits_df, credits_df, file_path, excluded_transactions).
    """
    saved_csvs = load_saved_csvs()
    if name in saved_csvs:
        file_info = saved_csvs[name]
        file_path = file_info['file_path']
        excluded_transactions = [tuple(item) for item in file_info.get('excluded_transactions', [])]

        df = pd.read_csv(file_path)

        debits_df, credits_df, _ = process_csv(self, df)  # Pass self to process_csv

        return debits_df, credits_df, file_path, excluded_transactions
    else:
        messagebox.showerror("Error", f"CSV file '{name}' not found.")
        return None, None, None, None


def append_csv_for_comparison(self, name, selected_csvs, load_csv_data, run_csv_comparison, process_csv,
                              load_saved_csvs):
    """
    Adds the selected CSV to the list for comparison using load_csv_data method.

    Parameters:
    name (str): The name of the CSV file to add.
    selected_csvs (list): A list of currently selected CSV files for comparison.
    load_csv_data (func): Function to load and process CSV data.
    run_csv_comparison (func): Function to run the comparison once two CSVs are selected.
    process_csv (func): Method to process a loaded CSV file.
    load_saved_csvs (func): Function to load saved CSVs.
    """
    if len(selected_csvs) < 2:
        debits_df, credits_df, file_path, excluded_transactions = load_csv_data(self, name, load_saved_csvs,
                                                                                process_csv)
        if debits_df is not None and credits_df is not None:
            filename = os.path.splitext(os.path.basename(file_path))[0]
            csv_data = (debits_df, credits_df, filename)
            selected_csvs.append((csv_data, excluded_transactions))

        if len(selected_csvs) == 2:
            return run_csv_comparison(selected_csvs)


def execute_csv_comparison(selected_csvs):
    """
    Loads the selected CSV files, compares them, and returns the results.
    """
    if len(selected_csvs) == 2:
        (debits_df1, credits_df1, file_name1), excluded_transactions1 = selected_csvs[0]
        (debits_df2, credits_df2, file_name2), excluded_transactions2 = selected_csvs[1]

        csv_data_list = [
            (debits_df1, credits_df1, file_name1),
            (debits_df2, credits_df2, file_name2)
        ]
        excluded_transactions_list = [excluded_transactions1, excluded_transactions2]

        comparison_results = compare_csvs(csv_data_list, excluded_transactions_list)

        # Clear selected CSVs after the comparison is done
        selected_csvs.clear()

        return comparison_results, file_name1, file_name2


def create_comparison_results(root, clear_widgets, results, file_name1, file_name2, create_widgets_callback,
                              show_comparison_summary):
    from UI import display_summary_statistics
    """
    Displays the debit and credit comparison results using the actual filenames.
    """
    clear_widgets()  # Use the clear_widgets function to clear the root

    title_label = ctk.CTkLabel(root, text="Comparison Results", font=("Helvetica", 30, "bold"))
    title_label.pack(pady=10)

    scrollable_frame = ctk.CTkScrollableFrame(root)
    scrollable_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

    # Debit Comparison Display - File 1 and File 2 side by side
    debit_file1_frame = ctk.CTkFrame(scrollable_frame)
    debit_file1_frame.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")

    debit_file2_frame = ctk.CTkFrame(scrollable_frame)
    debit_file2_frame.grid(row=0, column=1, padx=20, pady=10, sticky="nsew")

    # Credit Comparison Display - File 1 and File 2 side by side
    credit_file1_frame = ctk.CTkFrame(scrollable_frame)
    credit_file1_frame.grid(row=0, column=2, padx=20, pady=10, sticky="nsew")

    credit_file2_frame = ctk.CTkFrame(scrollable_frame)
    credit_file2_frame.grid(row=0, column=3, padx=20, pady=10, sticky="nsew")

    # Titles for each file's data using the actual filenames
    debits_title1 = ctk.CTkLabel(debit_file1_frame, text=f"Debits - {file_name1}",
                                 font=("Helvetica", 25, "bold"))
    debits_title1.pack(anchor="center", pady=10)

    debits_title2 = ctk.CTkLabel(debit_file2_frame, text=f"Debits - {file_name2}",
                                 font=("Helvetica", 25, "bold"))
    debits_title2.pack(anchor="center", pady=10)

    credits_title1 = ctk.CTkLabel(credit_file1_frame, text=f"Credits - {file_name1}",
                                  font=("Helvetica", 25, "bold"))
    credits_title1.pack(anchor="center", pady=10)

    credits_title2 = ctk.CTkLabel(credit_file2_frame, text=f"Credits - {file_name2}",
                                  font=("Helvetica", 25, "bold"))
    credits_title2.pack(anchor="center", pady=10)

    # Populate the grids for Debits (File 1 and File 2 side by side)
    for category, total1, total2 in results['debits']['category_comparisons']:
        label1 = ctk.CTkLabel(debit_file1_frame,
                              text=f"Category: {category} | Amount: {total1}",
                              font=("Helvetica", 20))
        label1.pack(anchor="w", padx=10)

        label2 = ctk.CTkLabel(debit_file2_frame,
                              text=f"Category: {category} | Amount: {total2}",
                              font=("Helvetica", 20))
        label2.pack(anchor="w", padx=10)

    # Display Debit summary statistics for File 1
    display_summary_statistics(debit_file1_frame, results['debits'], file_name1, is_credit=False)

    # Display Debit summary statistics for File 2
    display_summary_statistics(debit_file2_frame, {
        'summary': results['debits']['summary_2'],
        'overall_min': results['debits']['overall_min_2'],
        'overall_max': results['debits']['overall_max_2'],
        'total_spent': results['debits']['total_spent_2'],
        'most_expensive': results['debits']['most_expensive_2'],
        'least_expensive': results['debits']['least_expensive_2']
    }, file_name2, is_credit=False)

    # Populate the grids for Credits (File 1 and File 2 side by side)
    for category, total1, total2 in results['credits']['category_comparisons']:
        label1 = ctk.CTkLabel(credit_file1_frame,
                              text=f"Category: {category} | Amount: {total1}",
                              font=("Helvetica", 20))
        label1.pack(anchor="w", padx=10)

        label2 = ctk.CTkLabel(credit_file2_frame,
                              text=f"Category: {category} | Amount: {total2}",
                              font=("Helvetica", 20))
        label2.pack(anchor="w", padx=10)

    # Display Credit summary statistics for File 1
    display_summary_statistics(credit_file1_frame, results['credits'], file_name1, is_credit=True)

    # Display Credit summary statistics for File 2
    display_summary_statistics(credit_file2_frame, {
        'summary': results['credits']['summary_2'],
        'overall_min': results['credits']['overall_min_2'],
        'overall_max': results['credits']['overall_max_2'],
        'total_made': results['credits']['total_made_2'],
        'most_profitable': results['credits']['most_profitable_2'],
        'least_profitable': results['credits']['least_profitable_2']
    }, file_name2, is_credit=True)

    # Button to go to the summary page
    summary_button = ctk.CTkButton(root, text="View Summary",
                                   command=lambda: show_comparison_summary(results, file_name1, file_name2))

    summary_button.pack(pady=10)
    back_button = ctk.CTkButton(root, text="Back", command=create_widgets_callback)
    back_button.pack(pady=10)


def create_comparison_summary(root, clear_widgets, results, file_name1, file_name2, create_widgets_callback):
    """
    Displays the comparison summary statistics using the actual filenames.
    """
    clear_widgets()  # Use the clear_widgets function to clear the root

    scrollable_frame = ctk.CTkScrollableFrame(root)
    scrollable_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=10)

    comparison_title = ctk.CTkLabel(scrollable_frame, text="Comparison Summary:", font=("Helvetica", 25, "bold"))
    comparison_title.pack(anchor="center", pady=10)

    # Part 1: Display Higher Amount for Each Category
    part1_title = ctk.CTkLabel(scrollable_frame, text="Part 1: Higher Amount for Each Category",
                               font=("Helvetica", 22, "bold"))
    part1_title.pack(anchor="center", pady=10)

    for comparison in ['debits', 'credits']:
        comparison_data = results[comparison]

        if not comparison_data['category_comparisons']:
            no_data_label = ctk.CTkLabel(scrollable_frame, text=f"No data available for {comparison.capitalize()}.",
                                         font=("Helvetica", 20))
            no_data_label.pack(anchor="w", padx=10, pady=5)
            continue

        for category, total1, total2 in comparison_data['category_comparisons']:
            # Compare using absolute values to determine higher amounts
            higher_file = file_name1 if abs(total1) > abs(total2) else file_name2
            higher_label = ctk.CTkLabel(scrollable_frame,
                                        text=f"Category: {category} - "
                                             f"Higher in {comparison.capitalize()}: {higher_file}",
                                        font=("Helvetica", 20))
            higher_label.pack(anchor="w", padx=10, pady=5)

    # Part 2: Display Smallest and Biggest Transactions
    part2_title = ctk.CTkLabel(scrollable_frame, text="Part 2: Smallest and Biggest Transactions",
                               font=("Helvetica", 22, "bold"))
    part2_title.pack(anchor="center", pady=10)

    for comparison in ['debits', 'credits']:
        comparison_data = results[comparison]

        if not comparison_data['category_comparisons']:
            no_data_label = ctk.CTkLabel(scrollable_frame, text=f"No data available for {comparison.capitalize()}.",
                                         font=("Helvetica", 20))
            no_data_label.pack(anchor="w", padx=10, pady=5)
            continue

        for category, total1, total2 in comparison_data['category_comparisons']:
            smallest_amount = min(abs(total1), abs(total2))
            smallest_file = file_name1 if abs(total1) == smallest_amount else file_name2
            smallest_label = ctk.CTkLabel(scrollable_frame,
                                          text=f"Category: {category} - Smallest Transaction ({comparison.capitalize()}"
                                               f"): {smallest_amount} ({smallest_file})",
                                          font=("Helvetica", 20))
            smallest_label.pack(anchor="w", padx=10, pady=5)

            biggest_amount = max(abs(total1), abs(total2))
            biggest_file = file_name1 if abs(total1) == biggest_amount else file_name2
            biggest_label = ctk.CTkLabel(scrollable_frame,
                                         text=f"Category: {category} - Biggest Transaction ({comparison.capitalize()}):"
                                              f"{biggest_amount} ({biggest_file})",
                                         font=("Helvetica", 20))
            biggest_label.pack(anchor="w", padx=10, pady=5)

    # Part 3: Display Most and Least Expensive Categories
    part3_title = ctk.CTkLabel(scrollable_frame, text="Part 3: Most and Least Expensive Categories",
                               font=("Helvetica", 22, "bold"))
    part3_title.pack(anchor="center", pady=10)

    for comparison in ['debits', 'credits']:
        comparison_data = results[comparison]

        if not comparison_data['category_comparisons']:
            no_data_label = ctk.CTkLabel(scrollable_frame, text=f"No data available for {comparison.capitalize()}.",
                                         font=("Helvetica", 20))
            no_data_label.pack(anchor="w", padx=10, pady=5)
            continue

        most_expensive_file1 = max(comparison_data['category_comparisons'], key=lambda x: abs(x[1]))
        most_expensive_file2 = max(comparison_data['category_comparisons'], key=lambda x: abs(x[2]))
        least_expensive_file1 = min(comparison_data['category_comparisons'], key=lambda x: abs(x[1]))
        least_expensive_file2 = min(comparison_data['category_comparisons'], key=lambda x: abs(x[2]))

        most_expensive_label_file1 = ctk.CTkLabel(scrollable_frame,
                                                  text=f"Most Expensive Category ({file_name1}"
                                                       f" - {comparison.capitalize()}): {most_expensive_file1[0]} - "
                                                       f"{abs(most_expensive_file1[1])}",
                                                  font=("Helvetica", 20))
        most_expensive_label_file1.pack(anchor="w", padx=10, pady=5)

        most_expensive_label_file2 = ctk.CTkLabel(scrollable_frame,
                                                  text=f"Most Expensive Category ({file_name2} "
                                                       f"- {comparison.capitalize()}): {most_expensive_file2[0]}"
                                                       f" - {abs(most_expensive_file2[2])}",
                                                  font=("Helvetica", 20))
        most_expensive_label_file2.pack(anchor="w", padx=10, pady=5)

        least_expensive_label_file1 = ctk.CTkLabel(scrollable_frame,
                                                   text=f"Least Expensive Category ({file_name1}"
                                                        f" - {comparison.capitalize()}): {least_expensive_file1[0]}"
                                                        f" - {abs(least_expensive_file1[1])}",
                                                   font=("Helvetica", 20))
        least_expensive_label_file1.pack(anchor="w", padx=10, pady=5)

        least_expensive_label_file2 = ctk.CTkLabel(scrollable_frame,
                                                   text=f"Least Expensive Category ({file_name2}"
                                                        f" - {comparison.capitalize()}): {least_expensive_file2[0]}"
                                                        f" - {abs(least_expensive_file2[2])}",
                                                   font=("Helvetica", 20))
        least_expensive_label_file2.pack(anchor="w", padx=10, pady=5)

    # Correctly pass back_callback and show_comparison_summary
    back_button = ctk.CTkButton(root, text="Back to Comparison",
                                command=lambda: create_comparison_results(root, clear_widgets, results, file_name1,
                                                                          file_name2, create_widgets_callback,
                                                                          create_comparison_summary))
    back_button.pack(pady=10)


def compare_csvs(csv_data_list, excluded_transactions_list):
    """
    Compares multiple CSV datasets (debits and credits) to provide detailed insights,
    only including the transactions that are not excluded for each specific file.

    Parameters:
    csv_data_list (list): A list of tuples, each containing (debits_df, credits_df, file_name).
    excluded_transactions_list (list): A list of excluded transactions lists for each CSV file.

    Returns:
    dict: A dictionary containing detailed comparison results between the datasets.
    """
    if len(csv_data_list) < 2 or len(excluded_transactions_list) != len(csv_data_list):
        return {}

    comparison_results = {
        'debits': {'category_comparisons': []},
        'credits': {'category_comparisons': []}
    }

    def filter_exclusions(df, transaction_type, excluded_set):
        return df[
            ~df.apply(lambda row: (row['Started Date'], row['Description'], transaction_type) in excluded_set, axis=1)]

    def calculate_individual_summary(filtered_debits_df, filtered_credits_df):
        debit_summary = filtered_debits_df.groupby('Category').agg(
            total_spending=('Debit', lambda x: round(abs(x.sum()), 2)),
            min_transaction=('Debit', lambda x: round(x.abs().min(), 2)),
            max_transaction=('Debit', lambda x: round(x.abs().max(), 2)),
            avg_transaction=('Debit', lambda x: round(x.abs().mean(), 2))
        ).reset_index() if 'Category' in filtered_debits_df.columns else pd.DataFrame(
            columns=['Category', 'total_spending', 'min_transaction', 'max_transaction', 'avg_transaction'])

        overall_min_debit = abs(filtered_debits_df['Debit']).min() if not filtered_debits_df.empty else None
        overall_max_debit = abs(filtered_debits_df['Debit']).max() if not filtered_debits_df.empty else None
        total_spent = abs(filtered_debits_df['Debit']).sum() if not filtered_debits_df.empty else 0

        most_expensive_debit_category = debit_summary.loc[
            debit_summary['total_spending'].idxmax()] if not debit_summary.empty else None
        least_expensive_debit_category = debit_summary.loc[
            debit_summary['total_spending'].idxmin()] if not debit_summary.empty else None

        credit_summary = filtered_credits_df.groupby('Category').agg(
            total_income=('Credit', lambda x: round(x.sum(), 2)),
            min_transaction=('Credit', lambda x: round(x.abs().min(), 2)),
            max_transaction=('Credit', lambda x: round(x.abs().max(), 2)),
            avg_transaction=('Credit', lambda x: round(x.abs().mean(), 2))
        ).reset_index() if 'Category' in filtered_credits_df.columns else pd.DataFrame(
            columns=['Category', 'total_income', 'min_transaction', 'max_transaction', 'avg_transaction'])

        overall_min_credit = filtered_credits_df['Credit'].abs().min() if not filtered_credits_df.empty else None
        overall_max_credit = filtered_credits_df['Credit'].abs().max() if not filtered_credits_df.empty else None
        total_made = filtered_credits_df['Credit'].sum() if not filtered_credits_df.empty else 0

        most_profitable_credit_category = credit_summary.loc[
            credit_summary['total_income'].idxmax()] if not credit_summary.empty else None
        least_profitable_credit_category = credit_summary.loc[
            credit_summary['total_income'].idxmin()] if not credit_summary.empty else None

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

    for i, ((debits_df1, credits_df1, _), (debits_df2, credits_df2, _)) in enumerate(
            zip(csv_data_list[:-1], csv_data_list[1:])):
        excluded_set1 = set(tuple(t) for t in excluded_transactions_list[i])
        excluded_set2 = set(tuple(t) for t in excluded_transactions_list[i + 1])

        filtered_debits_df1 = filter_exclusions(debits_df1, 'Debit', excluded_set1)
        filtered_debits_df2 = filter_exclusions(debits_df2, 'Debit', excluded_set2)
        filtered_credits_df1 = filter_exclusions(credits_df1, 'Credit', excluded_set1)
        filtered_credits_df2 = filter_exclusions(credits_df2, 'Credit', excluded_set2)

        summary1 = calculate_individual_summary(filtered_debits_df1, filtered_credits_df1)
        summary2 = calculate_individual_summary(filtered_debits_df2, filtered_credits_df2)

        debit_categories = set(
            filtered_debits_df1['Category'].dropna().unique()) if not filtered_debits_df1.empty else set()
        debit_categories.update(
            set(filtered_debits_df2['Category'].dropna().unique()) if not filtered_debits_df2.empty else set())

        for category in debit_categories:
            total1 = filtered_debits_df1[filtered_debits_df1['Category'] == category][
                'Debit'].sum() if not filtered_debits_df1.empty and category in filtered_debits_df1[
                'Category'].values else 0
            total2 = filtered_debits_df2[filtered_debits_df2['Category'] == category][
                'Debit'].sum() if not filtered_debits_df2.empty and category in filtered_debits_df2[
                'Category'].values else 0
            comparison_results['debits']['category_comparisons'].append((category, total1, total2))

        credit_categories = set(
            filtered_credits_df1['Category'].dropna().unique()) if not filtered_credits_df1.empty else set()
        credit_categories.update(
            set(filtered_credits_df2['Category'].dropna().unique()) if not filtered_credits_df2.empty else set())

        for category in credit_categories:
            total1 = filtered_credits_df1[filtered_credits_df1['Category'] == category][
                'Credit'].sum() if not filtered_credits_df1.empty and category in filtered_credits_df1[
                'Category'].values else 0
            total2 = filtered_credits_df2[filtered_credits_df2['Category'] == category][
                'Credit'].sum() if not filtered_credits_df2.empty and category in filtered_credits_df2[
                'Category'].values else 0
            comparison_results['credits']['category_comparisons'].append((category, total1, total2))

        comparison_results['debits'].update(summary1['debits'])
        comparison_results['credits'].update(summary1['credits'])

        comparison_results['debits'].update({
            'summary_2': summary2['debits']['summary'],
            'overall_min_2': summary2['debits']['overall_min'],
            'overall_max_2': summary2['debits']['overall_max'],
            'total_spent_2': summary2['debits']['total_spent'],
            'most_expensive_2': summary2['debits']['most_expensive'],
            'least_expensive_2': summary2['debits']['least_expensive']
        })

        comparison_results['credits'].update({
            'summary_2': summary2['credits']['summary'],
            'overall_min_2': summary2['credits']['overall_min'],
            'overall_max_2': summary2['credits']['overall_max'],
            'total_made_2': summary2['credits']['total_made'],
            'most_profitable_2': summary2['credits']['most_profitable'],
            'least_profitable_2': summary2['credits']['least_profitable']
        })

    return comparison_results
