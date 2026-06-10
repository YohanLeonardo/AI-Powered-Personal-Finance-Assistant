from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
from datetime import datetime
from utils import data_manager, llm_utils, visualization_utils

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "my_secret_key")

@app.template_filter('markdown')
def markdown_filter(text):
    # This filter converts simple markdown text (bold ** and bullet points * or -) into HTML.
    # It is useful for displaying formatted AI responses on the page.
    if not text:
        return ""
    import re
    # Replace **text** with strong tag
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    lines = text.split('\n')
    in_list = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        # Check if the line is a list item
        if stripped.startswith('* ') or stripped.startswith('- '):
            if not in_list:
                new_lines.append('<ul style="margin-left: 1.5em; list-style-type: disc; margin-bottom: 1em;">')
                in_list = True
            new_lines.append(f'<li style="margin-bottom: 0.5em;">{stripped[2:]}</li>')
        else:
            # If list ends, close the ul tag
            if in_list:
                new_lines.append('</ul>')
                in_list = False
            if stripped:
                new_lines.append(f'<p style="margin-bottom: 1em;">{stripped}</p>')
    if in_list:
        new_lines.append('</ul>')
    return '\n'.join(new_lines)

# Main page: Shows the dashboard and charts
@app.route('/')
def index():
    transactions = data_manager.get_transactions()
    budgets = data_manager.get_budgets()
    
    # Create charts to show on the page
    expense_chart = visualization_utils.create_expense_pie_chart(transactions)
    budget_chart = visualization_utils.create_budget_vs_actual_chart(budgets, transactions)
    
    total_spent = sum(t['amount'] if t.get('category') != 'Savings' else -t['amount'] for t in transactions)
    income = budgets.get('income', 0)
    saldo = income - total_spent
    
    # Generate spending insights
    insights = llm_utils.get_spending_insights(budgets, transactions)
    
    return render_template('index.html', 
                           saldo=saldo, 
                           expense_chart=expense_chart, 
                           budget_chart=budget_chart,
                           insights=insights)

# Budget page: Set monthly income and category limits
@app.route('/budget', methods=['GET', 'POST'])
def budget():
    if request.method == 'POST':
        # Get data from the form
        categories = ['Needs', 'Wants', 'Savings']
        new_budgets = {cat: float(request.form.get(cat, 0)) for cat in categories}
        
        # Get optional income value
        income_val = request.form.get('income')
        if income_val:
            new_budgets['income'] = float(income_val)
            
        data_manager.save_budgets(new_budgets)
        flash('Budget saved!')
        return redirect(url_for('budget'))
    
    budgets = data_manager.get_budgets()
    return render_template('budget.html', budgets=budgets)

# API Route: AI budget recommendation
@app.route('/api/recommend-budget', methods=['GET', 'POST'])
def recommend_budget():
    income_val = request.args.get('income') or (request.json.get('income') if request.is_json else None)
    if not income_val:
        return jsonify({"error": "Missing income parameter"}), 400
    try:
        income = float(income_val)
        recommendation = llm_utils.get_budget_recommendation(income)
        return jsonify(recommendation)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Savings Route: Create and view savings goals
@app.route('/savings', methods=['GET', 'POST'])
def savings():
    # Calculate current saldo
    transactions = data_manager.get_transactions()
    budgets = data_manager.get_budgets()
    total_spent = sum(t['amount'] if t.get('category') != 'Savings' else -t['amount'] for t in transactions)
    income = budgets.get('income', 0)
    saldo = income - total_spent

    if request.method == 'POST':
        goal_name = request.form.get('goal_name')
        target_amount = float(request.form.get('target_amount', 0))
        target_date = request.form.get('target_date')
        
        goal = {
            "goal_name": goal_name,
            "target_amount": target_amount,
            "current_amount": saldo, # automatically set to current saldo
            "target_date": target_date
        }
        data_manager.save_savings_goal(goal)
        flash('Savings goal added!')
        return redirect(url_for('savings'))
        
    goals = data_manager.get_savings_goals()
    # Update current amount for each goal to reflect active balance
    for goal in goals:
        goal['current_amount'] = saldo
        
    return render_template('savings.html', goals=goals, saldo=saldo)

# Route to complete / delete a savings goal
@app.route('/complete-goal/<int:goal_idx>', methods=['GET', 'POST'])
def complete_goal(goal_idx):
    goals = data_manager.get_savings_goals()
    if 0 <= goal_idx < len(goals):
        goal = goals[goal_idx]
        target_amount = goal.get('target_amount', 0)
        goal_name = goal.get('goal_name', 'Unnamed Goal')
        
        # Deduct target amount from balance by saving a transaction
        data_manager.save_transaction({
            'description': f"Completed Goal: {goal_name}",
            'amount': target_amount,
            'category': 'Needs', 
            'date': datetime.now().strftime("%Y-%m-%d")
        })
        
        # Now delete the goal from our local JSON goal database.
        if data_manager.delete_savings_goal(goal_idx):
            flash(f"Congratulations! Goal '{goal_name}' completed and Rp {target_amount:,.0f} deducted from your balance.")
    else:
        flash('Goal not found.')
    return redirect(url_for('savings'))

# API Route: Get AI Investment Guidance for a Savings Goal
@app.route('/api/savings-guidance/<int:goal_idx>')
def savings_guidance(goal_idx):
    goals = data_manager.get_savings_goals()
    if goal_idx < 0 or goal_idx >= len(goals):
        return jsonify({"error": "Goal not found"}), 404
        
    # Calculate current saldo
    transactions = data_manager.get_transactions()
    budgets = data_manager.get_budgets()
    total_spent = sum(t['amount'] if t.get('category') != 'Savings' else -t['amount'] for t in transactions)
    income = budgets.get('income', 0)
    saldo = income - total_spent
    
    goal = goals[goal_idx]
    guidance = llm_utils.get_investment_guidance(
        goal['goal_name'],
        goal['target_amount'],
        saldo, # pass current saldo instead of saved current_amount
        goal['target_date']
    )
    return jsonify({"guidance": guidance})

# Report Generation Route: Detailed printable HTML report
@app.route('/generate-report')
def generate_report():
    transactions = data_manager.get_transactions()
    budgets = data_manager.get_budgets()
    goals = data_manager.get_savings_goals()
    insights = llm_utils.get_spending_insights(budgets, transactions)
    
    total_spent = sum(t['amount'] if t.get('category') != 'Savings' else -t['amount'] for t in transactions)
    income = budgets.get('income', 0)
    saldo = income - total_spent
    
    # Calculate category limits
    category_limits = {}
    for cat in ['Needs', 'Wants', 'Savings']:
        category_limits[cat] = budgets.get(cat, 0)
        
    # Calculate actual spending by category
    actual_spent = {cat: 0.0 for cat in ['Needs', 'Wants', 'Savings']}
    for t in transactions:
        cat = t.get('category')
        if cat in actual_spent:
            actual_spent[cat] += t['amount']
            
    return render_template('report.html',
                           transactions=transactions,
                           budgets=budgets,
                           goals=goals,
                           insights=insights,
                           saldo=saldo,
                           category_limits=category_limits,
                           actual_spent=actual_spent,
                           datetime_now=datetime.now().strftime("%Y-%m-%d %H:%M"))

# Chatbot page: Ask AI for financial advice
@app.route('/ai-advisor', methods=['GET', 'POST'])
def ai_advisor():
    # Handle GET request (loading the page initially)
    if request.method == 'GET':
        return render_template('chatbot.html', ai_response=None)
        
    # Handle API request from the JS frontend (for What-If Simulator)
    if request.is_json:
        user_query = request.json.get('message')
        
        # Load data context
        budgets = data_manager.get_budgets()
        transactions = data_manager.get_transactions()
        
        # Get advice from LLM
        ai_response = llm_utils.get_personalized_advice(user_query, budgets, transactions)
        
        return jsonify({"response": ai_response})
        
    # Fallback for standard HTML form submission
    user_query = request.form.get('query')
    budgets = data_manager.get_budgets()
    transactions = data_manager.get_transactions()
    
    ai_response = llm_utils.get_personalized_advice(user_query, budgets, transactions)
    
    return render_template('chatbot.html', ai_response=ai_response)

# Action: Add a new expense
@app.route('/add-transaction', methods=['POST'])
def add_transaction():
    description = request.form.get('description')
    amount = float(request.form.get('amount'))
    category = request.form.get('category')
    date = datetime.now().strftime("%Y-%m-%d")
    
    # Save to JSON file
    data_manager.save_transaction({
        'description': description,
        'amount': amount,
        'category': category,
        'date': date
    })
    
    flash('Transaction added!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)