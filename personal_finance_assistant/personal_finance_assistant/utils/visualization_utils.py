import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import pandas as pd

STATIC_IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'img')

def ensure_img_dir():
    if not os.path.exists(STATIC_IMG_DIR):
        os.makedirs(STATIC_IMG_DIR)

def create_expense_pie_chart(transactions):
    if not transactions:
        return None
    
    ensure_img_dir()
    df = pd.DataFrame(transactions)
    if 'category' not in df.columns or 'amount' not in df.columns:
        return None
        
    category_totals = df.groupby('category')['amount'].sum()
    
    plt.figure(figsize=(8, 6))
    category_totals.plot(kind='pie', autopct='%1.1f%%', startangle=140)
    plt.title('Expenses by Category')
    plt.ylabel('')
    
    img_path = os.path.join(STATIC_IMG_DIR, 'expense_pie.png')
    plt.savefig(img_path)
    plt.close()
    return 'img/expense_pie.png'

def create_budget_vs_actual_chart(budgets, transactions):
    if not budgets or not transactions:
        return None
        
    ensure_img_dir()
    df_trans = pd.DataFrame(transactions)
    actual_totals = df_trans.groupby('category')['amount'].sum().to_dict()
    
    categories = list(budgets.keys())
    budget_values = [budgets[cat] for cat in categories]
    actual_values = [actual_totals.get(cat, 0) for cat in categories]
    
    plt.figure(figsize=(10, 6))
    x = range(len(categories))
    width = 0.35
    
    plt.bar(x, budget_values, width, label='Budgeted')
    plt.bar([i + width for i in x], actual_values, width, label='Actual')
    
    plt.xlabel('Category')
    plt.ylabel('Amount')
    plt.title('Budget vs Actual Spending')
    plt.xticks([i + width/2 for i in x], categories)
    plt.legend()
    
    img_path = os.path.join(STATIC_IMG_DIR, 'budget_vs_actual.png')
    plt.savefig(img_path)
    plt.close()
    return 'img/budget_vs_actual.png'
