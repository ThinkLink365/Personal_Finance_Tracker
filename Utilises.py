# Utilises.py
import csv
import os
import json
import re
import shutil
import webbrowser

SAVED_CSVS_FILE = 'saved_csvs.json'
CSV_STORAGE_DIR = 'saved_csvs'
CATEGORY_MAP_FILE = 'category_map.json'


def load_category_map():
    if os.path.exists(CATEGORY_MAP_FILE):
        with open(CATEGORY_MAP_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_category_map(category_map):
    with open(CATEGORY_MAP_FILE, 'w') as f:
        json.dump(category_map, f, indent=4)


def add_keyword_to_category(category, keyword):
    category_map = load_category_map()
    if category not in category_map:
        category_map[category] = []
    if keyword not in category_map[category]:
        category_map[category].append(keyword)
        save_category_map(category_map)
        return True
    return False


def delete_category(category):
    category_map = load_category_map()
    if category in category_map:
        del category_map[category]
        save_category_map(category_map)
        return True
    return False


def delete_keyword_from_category(category, keyword):
    category_map = load_category_map()
    if category in category_map and keyword in category_map[category]:
        category_map[category].remove(keyword)
        if not category_map[category]:
            del category_map[category]
        save_category_map(category_map)
        return True
    return False


def save_csv_content(file_path, name, excluded_transactions=None):
    excluded_transactions = excluded_transactions or []

    if not os.path.exists(CSV_STORAGE_DIR):
        os.makedirs(CSV_STORAGE_DIR)

    new_file_path = os.path.join(CSV_STORAGE_DIR, f"{name}.csv")

    # Only copy if the file paths are different
    if file_path != new_file_path:
        shutil.copy(file_path, new_file_path)

    # Update CSV content by removing excluded transactions
    updated_rows = []
    with open(file_path, 'r', newline='', encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        headers = next(reader)
        updated_rows.append(headers)
        for row in reader:
            if row[0] not in excluded_transactions:
                updated_rows.append(row)

    with open(new_file_path, 'w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(updated_rows)

    # Update the metadata JSON file
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

        data[name] = {
            'file_path': new_file_path,
            'excluded_transactions': excluded_transactions
        }

        f.seek(0)
        f.truncate()
        json.dump(data, f, indent=4)


def load_saved_csvs():
    if not os.path.exists(SAVED_CSVS_FILE):
        return {}

    with open(SAVED_CSVS_FILE, 'r') as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError:
            return {}


def delete_saved_csv(name):
    if not os.path.exists(SAVED_CSVS_FILE):
        return

    with open(SAVED_CSVS_FILE, 'r+') as f:
        try:
            data = json.load(f)
            if name in data:
                os.remove(data[name]['file_path'])
                del data[name]
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=4)
        except json.JSONDecodeError:
            pass


def categorize(description):
    category_map = load_category_map()
    description = description.lower().strip()
    description = re.sub(r'\s+', ' ', description)
    for category, keywords in category_map.items():
        for keyword in keywords:
            pattern = re.compile(re.escape(keyword.lower()))
            if pattern.search(description):
                return category.capitalize()
    return "Other"


def open_website(url):
    webbrowser.open_new(url)
