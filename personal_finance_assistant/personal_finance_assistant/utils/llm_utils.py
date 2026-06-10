import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize the new GenAI client using the key from .env
# The client automatically looks for the GEMINI_API_KEY environment variable,
# but passing it explicitly is a safe practice.
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_personalized_advice(query, budgets, transactions):
    """
    Generates personalized financial advice and What-If simulations.
    Strictly utilizes Gemini (gemini-3.1-flash-lite) via the new google.genai SDK.
    """
    try:
        # Convert data structures to JSON strings so the LLM can easily parse them
        budget_context = json.dumps(budgets, indent=2)
        transaction_context = json.dumps(transactions, indent=2)
        
        # Assemble the System Prompt according to the Implementation Plan
        system_prompt = f"""
        You are a smart, assertive, and highly solution-oriented AI Financial Advisor.
        
        Current User Financial Context:
        - Budget Allocations (Income, Needs, Wants, Savings): {budget_context}
        - Recent Transactions: {transaction_context}
        
        Important Instructions:
        1. Provide specific advice strictly grounded in the Financial Context data provided above.
        2. WHAT-IF SIMULATIONS: If the user requests a scenario simulation (such as buying an item on installments or planning a vacation), you MUST PERFORM EXPLICIT MATHEMATICAL CALCULATIONS (e.g., Total Price / Number of Months = Monthly Installment).
        3. EVALUATION: Compare the new installment or expense amount against the user's remaining 'Wants' or 'Needs' category limits. Clearly explain its impact on cash flow and 'Savings' targets.
        4. FORMATTING: Maximize the use of Markdown. Use tables for numerical breakdowns, bullet points for lists, and **bold** text for important metrics or warnings to ensure high readability on the web interface.
        """
        
        # Execute the user's prompt using the new client.models.generate_content structure
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
            )
        )
        
        return response.text
        
    except Exception as e:
        # Return a cleanly formatted error message in case of API or connection issues
        return f"**Error:** Sorry, the AI Advisor is currently unavailable. Technical details: `{str(e)}`"

def get_budget_recommendation(income):
    """
    Recommends a custom percentage split based on the user's monthly income.
    """
    try:
        prompt = f"""
        Given a monthly income of {income}, recommend a custom budget allocation.
        Return your response strictly as a JSON object with the following keys:
        - "Needs": percentage (integer, e.g. 50)
        - "Wants": percentage (integer, e.g. 30)
        - "Savings": percentage (integer, e.g. 20)
        - "Rationale": a short sentence explanation of the recommended ratio (e.g. "We recommend the standard 50/30/20 rule to balance essentials, personal desires, and future savings.")
        Ensure the percentages sum up to exactly 100. Do not include markdown code block formatting (like ```json). Just return raw JSON.
        """
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)
    except Exception as e:
        return {
            "Needs": 50,
            "Wants": 30,
            "Savings": 20,
            "Rationale": f"Using default 50/30/20 rules. (AI service error: {str(e)})"
        }

def get_spending_insights(budgets, transactions):
    """
    Analyzes transaction category-wise spending and compares against budgets.
    """
    try:
        if not transactions:
            return "No recent transactions found. Add transactions on the dashboard to generate AI spending insights!"
            
        budget_context = json.dumps(budgets, indent=2)
        transaction_context = json.dumps(transactions, indent=2)
        
        prompt = f"""
        Analyze the user's spending habits.
        Budget Limits: {budget_context}
        Recent Transactions: {transaction_context}
        
        Provide 3 short, actionable, bullet-pointed insights or warnings regarding their spending compared to their budget limits.
        Be concise and helpful. Use Markdown.
        """
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Unable to generate AI insights at this moment. ({str(e)})"

def get_investment_guidance(goal_name, target_amount, current_amount, target_date):
    """
    Generates step-by-step novice investment recommendations for a savings goal.
    """
    try:
        prompt = f"""
        Help a beginner investor plan for a savings goal.
        Goal Name: {goal_name}
        Target Amount: {target_amount}
        Current Savings: {current_amount}
        Target Date: {target_date}
        
        Provide beginner-friendly investment suggestions and a step-by-step plan to achieve this goal effectively.
        Keep it structured using bullet points and tables where appropriate. Use Markdown.
        """
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Unable to generate investment guidance: {str(e)}"