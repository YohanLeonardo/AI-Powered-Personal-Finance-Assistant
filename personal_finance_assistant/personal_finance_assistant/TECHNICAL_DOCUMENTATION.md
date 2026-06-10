# Technical Documentation: AI Personal Finance Assistant

## 1. Introduction
This application is a local-first personal finance tracker and planner powered by Gemini AI. It helps users input daily expenses, plan category budgets, and save for specific goals while getting advice from an AI agent.

### Project Goals
- Make budgeting easy.
- Provide charts that show financial status.
- Integrate Gemini AI to recommend budgets, give investment strategies, and answer financial questions.
- Support completing savings goals, which automatically records a transaction to decrease the active balance.

## 2. Technical Stack
- **Backend:** Python 3.11 with Flask framework.
- **Frontend:** HTML5, CSS3, FontAwesome, JavaScript, and custom styling based on template layouts.
- **AI Engine:** Gemini API via python-based SDK helper.
- **Charts:** Matplotlib (rendered to Base64 image strings to display dynamically in HTML).
- **Database:** Local JSON files located in the `data/` directory (`budgets.json`, `transactions.json`, `savings_goals.json`).

## 3. Directory Structure
```text
personal_finance_assistant/
├── app.py                     # Main Flask application with all routes
├── requirements.txt           # Python dependency packages list
├── utils/
│   ├── data_manager.py        # Read/Write helper for local JSON databases
│   ├── llm_utils.py           # Gemini API wrappers and prompt configurations
│   └── visualization_utils.py # Matplotlib pie chart and comparison chart logic
├── static/
│   ├── css/
│   │   ├── main.css           # Global layout stylesheet (with custom resets)
│   │   └── chatbot.css        # Specific chatbot layout styling
│   └── js/
│       └── main.js            # General frontend javascript behavior
└── templates/
    ├── layout.html            # Core HTML base template (header, navigation menu)
    ├── index.html             # Homepage dashboard showing active saldo and charts
    ├── budget.html            # Category budget planning page
    ├── savings.html           # Savings goal listing and investment guidance page
    ├── chatbot.html           # Conversational AI chatbot UI
    └── report.html            # Printable HTML financial report layout
```

## 4. Key Logic Implementations

### Saldo & Spending Calculation
Active balance (saldo) is calculated dynamically from the income minus total spending:
```python
total_spent = sum(t['amount'] if t.get('category') != 'Savings' else -t['amount'] for t in transactions)
saldo = income - total_spent
```
*Note: Transactions in the 'Savings' category are treated as positive returns to saldo or savings fund allocation, while other categories deduct from the balance.*

### Goal Completion
When a savings goal is marked as finished, the system deletes the goal from the JSON database and saves a new transaction of category `Needs` with the goal's target amount. This reduces the user's active saldo automatically to show the money has been spent.

### Chart Rendering
The file `utils/visualization_utils.py` uses Matplotlib to generate charts, saving them into memory buffers as PNG and encoding to Base64 so they can be injected directly into `<img>` tags on the dashboard:
```python
buf = io.BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight')
buf.seek(0)
image_base64 = base64.b64encode(buf.read()).decode('utf-8')
```

## 5. Setup and Running
1. Rename `.env.example` to `.env` and configure your API key.
2. Install Python packages: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Access the site locally at `http://127.0.0.1:5000`
