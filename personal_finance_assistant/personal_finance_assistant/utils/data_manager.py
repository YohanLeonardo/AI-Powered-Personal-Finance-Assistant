import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def get_file_path(filename):
    return os.path.join(DATA_DIR, filename)

def load_json(filename, default=[]):
    path = get_file_path(filename)
    if not os.path.exists(path):
        return default
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception:
        return default

def save_json(filename, data):
    ensure_data_dir()
    path = get_file_path(filename)
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)

# Specific helpers
def get_transactions():
    return load_json('transactions.json')

def save_transaction(transaction):
    transactions = get_transactions()
    transactions.append(transaction)
    save_json('transactions.json', transactions)

def get_budgets():
    return load_json('budgets.json', default={})

def save_budgets(budgets):
    save_json('budgets.json', budgets)

def get_savings_goals():
    return load_json('savings_goals.json')

def save_savings_goal(goal):
    goals = get_savings_goals()
    goals.append(goal)
    save_json('savings_goals.json', goals)

def delete_savings_goal(index):
    goals = get_savings_goals()
    if 0 <= index < len(goals):
        goals.pop(index)
        save_json('savings_goals.json', goals)
        return True
    return False
