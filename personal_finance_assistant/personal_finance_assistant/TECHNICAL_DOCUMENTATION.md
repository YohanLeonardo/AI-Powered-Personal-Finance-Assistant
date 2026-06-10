# Technical Documentation: AI Personal Finance Assistant

## 1. Introduction
This project is a simple personal finance tracker app. It runs locally and uses Gemini AI to give financial advice. Users can input their daily transactions, set budget limits, and make savings goals.

### Project Goals
- Help users do budgeting easily.
- Show charts for spending overview.
- Use Gemini AI to give budget recommendation, investment advice, and answer questions.
- Automatically add expense transaction when user finishes a savings goal.

## 2. Technical Stack
- **Backend:** Python 3.11 with Flask framework.
- **Frontend:** HTML, CSS, JavaScript, and FontAwesome for icons.
- **AI Integration:** Google GenAI SDK (using gemini-3.1-flash-lite).
- **Charts:** Matplotlib (saved as PNG files in static folder).
- **Data Storage:** Local JSON files (`data/budgets.json`, `data/transactions.json`, and `data/savings_goals.json`).

## 3. Directory Structure
Here is how the project files are organized:
```text
personal_finance_assistant/
├── app.py                     # Main Flask routes and server logic
├── requirements.txt           # Python packages needed
├── .gitignore                 # Files to ignore in Git (like secrets and cache)
├── utils/
│   ├── data_manager.py        # Read and write to JSON files
│   ├── llm_utils.py           # Gemini API setup and prompts
│   └── visualization_utils.py # Chart generation using Matplotlib
├── static/
│   ├── css/
│   │   ├── main.css           # Global website styling
│   │   └── chatbot.css        # Chat page styling
│   └── js/
│       └── main.js            # Frontend JavaScript behavior
└── templates/
    ├── layout.html            # Main base layout template
    ├── index.html             # Dashboard with transactions and charts
    ├── budget.html            # Page to set budget and get AI recommendations
    ├── savings.html           # Savings page with goals list
    ├── chatbot.html           # Chatbot helper interface
    └── report.html            # Financial report page for printing
```

## 4. Key Logic and Features

### Balance and Saldo Calculation
The active balance (saldo) is calculated dynamically. We sum up the transactions and subtract them from income. 
But if the category is 'Savings', we treat it differently. Here is the code in `app.py`:
```python
total_spent = sum(t['amount'] if t.get('category') != 'Savings' else -t['amount'] for t in transactions)
saldo = income - total_spent
```
*Note: Transactions with category 'Savings' do not reduce the active balance.*

### Goal Completion
When the user clicks the "Finish Goal" button, the app does two things:
1. Deletes the goal from the JSON file.
2. Automatically creates a new transaction under category `Needs` with the goal's target amount. This is to reduce the active balance so it shows the money is actually spent.

### Chart Rendering
The file `utils/visualization_utils.py` uses Matplotlib to generate pie charts and bar charts. It saves the charts as PNG images directly into the static folder:
```python
img_path = os.path.join(STATIC_IMG_DIR, 'expense_pie.png')
plt.savefig(img_path)
plt.close()
```
Then, the frontend page displays these images using standard Flask `url_for('static', filename=...)`.

## 5. Setup and How to Run
1. Copy `.env.example` file and rename it to `.env`.
2. Open `.env` and fill the `GEMINI_API_KEY` with your Gemini API key.
3. Install the python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the backend app:
   ```bash
   python app.py
   ```
5. Open your web browser and go to: `http://127.0.0.1:5000`
