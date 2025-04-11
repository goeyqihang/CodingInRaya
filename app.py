# app.py
import os
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, url_for
import traceback
import re

# Import functions from our modules
from data_utils import load_provided_data
from analysis import (
    get_popular_items_by_frequency,
    get_sales_summary,
    get_popular_cuisines_in_city
    # get_low_performing_items is defined in analysis.py but not imported/used here now
)

load_dotenv()

# --- Initialize Data ---
datasets = None
data_loaded_successfully = False
try:
    print("App: Attempting to load data via data_utils...")
    datasets = load_provided_data()
    if datasets:
        data_loaded_successfully = True
        print("App ✅: Data loaded successfully via data_utils.")
    else:
        data_loaded_successfully = False
        print("App ❌: Data loading failed.")
except Exception as e:
    print(f"App ❌: Critical error during initial data load call: {e}")
    traceback.print_exc()
    data_loaded_successfully = False
    datasets = None

# --- Flask App Setup ---
app = Flask(__name__)

# --- OpenAI Config ---
openai_configured = False
try:
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key: raise ValueError("OPENAI_API_KEY not found in .env file.")
    openai.api_key = openai_api_key
    print("App ✅: OpenAI API Key configured successfully.")
    openai_configured = True
except Exception as e:
    print(f"App ❌: Error configuring OpenAI: {e}")
    openai_configured = False

# --- Helper Function ---
def parse_time_period(user_message_lower):
    """Parses user message to determine the desired time period (in English)."""
    if re.search(r'last 3 months|past 90 days', user_message_lower): return "last_90_days"
    if re.search(r'last month|past 30 days', user_message_lower): return "last_30_days"
    if re.search(r'last week|past 7 days', user_message_lower): return "last_7_days"
    if any(k in user_message_lower for k in ["recommend", "suggestion", "what to sell", "startup", "new merchant", "regional", "area", "profit", "earnings"]):
         return "last_90_days"
    return "last_30_days"

# --- Page Routes ---
@app.route('/')
def home(): return render_template('index.html', request=request)
@app.route('/chat')
def chat_page(): return render_template('chat.html', request=request)

# --- API Route ---
print("--- Flask is attempting to define the /api/interact-llm route NOW ---")
@app.route('/api/interact-llm', methods=['POST'])
def handle_llm_interaction():
    global datasets, data_loaded_successfully, openai_configured

    if not openai_configured: return jsonify({'error': 'OpenAI API Key not configured.'}), 500
    if not data_loaded_successfully or datasets is None: return jsonify({'error': 'Server data is not available.'}), 500

    try:
        req_data = request.get_json()
        if not req_data or 'message' not in req_data: return jsonify({'error': 'Missing message in request body'}), 400

        user_message = req_data['message']
        user_message_lower = user_message.lower()
        print(f"App: Received message: {user_message}")

        merchant_id_to_query = "3e2b6" # !!! EXAMPLE ID !!!
        city_id_to_query = '8'         # !!! EXAMPLE ID !!!
        city_name_map = {'8': 'Subang Jaya'}
        city_name_context = f"{city_name_map.get(city_id_to_query, f'City ID {city_id_to_query}')}"

        data_context = ""
        intent_recognized = False
        response_data = {}

        # --- Keywords ---
        popular_item_keywords = ["popular", "hot selling", "best selling", "top items"]
        sales_keywords = ["sale", "sales", "revenue", "performance", "income", "order value", "summary"]
        regional_rec_keywords = ["recommend", "suggestion", "what to sell", "suitable products", "new merchant", "startup", "regional", "area", "city", "location", "cuisine"]
        profit_keywords = ["profit", "increase profit", "improve profit", "earnings", "make money", "bottom line", "profitability"] # Could add "improve sales" here later

        # --- Intent Recognition Logic ---

        # Intent 1: Profit Improvement (Simplified Context)
        if any(p in user_message_lower for p in profit_keywords):
            intent_recognized = True
            print(f"App: Intent recognized: Profit improvement query for merchant {merchant_id_to_query}")
            time_period_arg = parse_time_period(user_message_lower)
            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
            days_to_query = days_map.get(time_period_arg, 90)

            print(f"App: Fetching data for simplified profit analysis (last {days_to_query} days)...")
            sales_summary = get_sales_summary(merchant_id_to_query, datasets, time_period_str=time_period_arg)
            popular_items = get_popular_items_by_frequency(merchant_id_to_query, datasets, days=days_to_query)
            # Low performing items are NOT calculated/included for this intent now

            # --- Combine SIMPLIFIED context ---
            context_parts = []
            context_parts.append("User wants advice on increasing profit (note: cost data is unavailable).")
            context_parts.append(f"Analysis based on data for merchant {merchant_id_to_query} over the last {days_to_query} days.")

            context_parts.append("\n--- Sales Summary ---")
            if isinstance(sales_summary, dict): context_parts.append(f"Period: {sales_summary['start_date']} to {sales_summary['end_date']}. Total Sales: ${sales_summary['total_sales']:,.2f}. Orders: {sales_summary['order_count']}.")
            elif isinstance(sales_summary, str): context_parts.append(f"Could not get sales summary: {sales_summary}.")
            else: context_parts.append("No recent sales data found.")

            context_parts.append(f"\n--- Popular Items (Top {len(popular_items) if isinstance(popular_items, list) else 'N/A'}) ---")
            if isinstance(popular_items, list) and popular_items:
                 # --- *** FIXED KEY HERE *** ---
                 items_text = "; ".join([f"{item['item_name']} ({item['unique_order_count']} unique orders)" for item in popular_items])
                 # --- *** END FIX *** ---
                 context_parts.append(f"{items_text}.")
            elif isinstance(popular_items, str): context_parts.append(f"Could not get popular items: {popular_items}.")
            else: context_parts.append("Could not determine popular items.")

            data_context = "\n".join(context_parts)
            print(f"App: Data Context (Profit Query - Simplified):\n{data_context}")
            # Fall through to LLM call

        # Intent 2: Popular Items (Specific Merchant)
        elif any(p in user_message_lower for p in popular_item_keywords) and not any(r in user_message_lower for r in regional_rec_keywords):
            intent_recognized = True
            print(f"App: Intent recognized: Popular items query for merchant {merchant_id_to_query}")
            time_period_arg = parse_time_period(user_message_lower)
            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
            days_to_query = days_map.get(time_period_arg, 30)
            popular_items_result = get_popular_items_by_frequency(merchant_id_to_query, datasets, days=days_to_query)

            if isinstance(popular_items_result, list) and popular_items_result:
                 # --- *** FIXED KEY HERE *** ---
                 items_text = ", ".join([f"{item['item_name']} ({item['unique_order_count']} unique orders)" for item in popular_items_result])
                 # --- *** END FIX *** ---
                 data_context = f"Data context for merchant {merchant_id_to_query} (popular items last {days_to_query} days by unique orders): Top {len(popular_items_result)} are: {items_text}. "
            elif isinstance(popular_items_result, str): data_context = f"Note on data context: Could not get popular items. Reason: {popular_items_result}. "
            else: data_context = f"Note on data context: No data for popular items (merchant {merchant_id_to_query}, last {days_to_query} days). "
            print(f"App: Data Context (Popular Items): {data_context}")
            # Fall through to LLM call

        # Intent 3: Sales Performance (Specific Merchant)
        elif any(s in user_message_lower for s in sales_keywords):
            intent_recognized = True
            print(f"App: Intent recognized: Sales performance query for merchant {merchant_id_to_query}")
            time_period_arg = parse_time_period(user_message_lower)
            sales_summary_result = get_sales_summary(merchant_id_to_query, datasets, time_period_str=time_period_arg)
            # Context formatting here doesn't use item frequency, so no change needed
            if isinstance(sales_summary_result, dict):
                start, end = sales_summary_result['start_date'], sales_summary_result['end_date']
                sales, count = sales_summary_result['total_sales'], sales_summary_result['order_count']
                data_context = f"Data context for merchant {merchant_id_to_query} (Sales Summary {start} to {end}): Total=${sales:,.2f}, Orders={count}. "
            elif isinstance(sales_summary_result, str): data_context = f"Note on data context: Could not get sales summary. Reason: {sales_summary_result}. "
            else: data_context = f"Note on data context: No sales data found (merchant {merchant_id_to_query}, period {time_period_arg}). "
            print(f"App: Data Context (Sales Summary): {data_context}")
             # Fall through to LLM call

        # Intent 4: Regional Cuisine Recommendation (New Merchant Context)
        elif any(r in user_message_lower for r in regional_rec_keywords) and ("new merchant" in user_message_lower or "what to sell" in user_message_lower or "startup" in user_message_lower or "recommend" in user_message_lower or "suggestion" in user_message_lower):
            intent_recognized = True
            print(f"App: Intent recognized: Regional cuisine recommendation for city {city_id_to_query}")
            time_period_arg = parse_time_period(user_message_lower)
            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
            days_to_query = days_map.get(time_period_arg, 90)
            popular_cuisines_result = get_popular_cuisines_in_city(city_id_to_query, datasets, days=days_to_query)
             # Context formatting here doesn't use item frequency, so no change needed
            if isinstance(popular_cuisines_result, list) and popular_cuisines_result:
                 cuisines_text = ", ".join(popular_cuisines_result)
                 data_context = f"Data context: User is asking for recommendations for a new merchant in {city_name_context}. Analysis of recent orders ({days_to_query} days) across merchants shows the top {len(popular_cuisines_result)} most frequent cuisine types are: {cuisines_text}. "
            elif isinstance(popular_cuisines_result, str): data_context = f"Note on data context: Could not get popular cuisines data for {city_name_context}. Reason: {popular_cuisines_result}. "
            else: data_context = f"Note on data context: Insufficient data for popular cuisine types in {city_name_context} (last {days_to_query} days). "
            print(f"App: Data Context (Regional Cuisines): {data_context}")
             # Fall through to LLM call

        # Fallback / General Query
        else:
            print("App: Intent: General query or not recognized.")
            data_context = "" # No specific data context generated
            # Fall through to LLM call


        # --- Build messages for OpenAI ---
        # --- System Prompt (Simplified for Profit Query) ---
        system_prompt = f"""
        You are MEX Assistant, an AI business advisor speaking directly TO a Grab merchant. Your purpose is to help the merchant (you) succeed by turning your data into understandable insights and actionable suggestions.

        VERY IMPORTANT: Always address the merchant directly using "you" and "your". Never refer to the merchant as 'the merchant' or by their ID in your response.

        Analyze the provided data context below to answer your specific question about your business. Go beyond just stating the numbers or list; interpret what they imply for your business. Where appropriate, suggest potential actions you could consider based on the data.

        --- Specific instructions for Profit Improvement query ---
        If the user asks how to increase profit:
        1. Start by clearly stating that direct profit calculation isn't possible due to missing cost data, so the advice focuses on improving potential profitability through revenue and efficiency.
        2. Briefly summarize your recent sales performance using the figures from the 'Sales Summary' section in the context.
        3. Discuss your popular items (using names and **unique order counts** from the 'Popular Items' section). Suggest specific ways you could leverage these (e.g., 'Consider promoting [Popular Item Name] which was in [N] **unique orders**...', potential bundling, ensuring stock).
        4. Synthesize these points: Explain how focusing on popular items might boost revenue.
        5. Conclude with general advice on reviewing pricing, menu diversity (without specific low-performer data), and operational efficiency.
        --- End of Profit Improvement instructions ---

        If you identify as a new merchant asking for advice on what to sell in {city_name_context}, use the popular cuisine data (if provided in the 'Regional Cuisine' context section) to suggest focusing on those categories, while also advising you to conduct general market research and differentiation.

        If no specific data context is available ('Data Context:' below is empty) or the context is just a note ('Note on data context: ...'), address your question directly. If it's a business question, answer from a general perspective, offering helpful advice to you. If it's a greeting or off-topic, respond naturally to you.
        If the context notes an error or lack of data ('Note on data context: Could not get...'), clearly communicate this limitation to you first before attempting a general answer.

        Be clear, concise, and focus on providing practical value to the merchant (you). Respond in English.

        Data Context:
        {data_context}
        """
        # --- End of System Prompt ---

        messages = [
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": user_message}
        ]
        print(f"App: --- Sending Messages to OpenAI ---")


        # --- Call OpenAI API ---
        try:
            completion = openai.chat.completions.create(
              model="gpt-4-turbo",
              messages=messages,
              temperature=0.5
            )
            llm_reply = completion.choices[0].message.content.strip()
            print(f"App: LLM Reply received successfully.")
            response_data['reply'] = llm_reply
        except Exception as e:
            print(f"App ❌: OpenAI API call failed: {e}")
            traceback.print_exc()
            response_data['reply'] = "Sorry, I encountered an issue trying to connect to the AI service. Please try again in a moment."

        # --- Return Response ---
        return jsonify(response_data)

    # --- Global Error Handling for the API Route ---
    except Exception as e:
        print(f"App ❌: An unexpected error occurred in /api/interact-llm: {e}")
        traceback.print_exc()
        return jsonify({'error': 'An unexpected error occurred on the server while processing your request.'}), 500


# --- Flask run ---
if __name__ == '__main__':
    if not data_loaded_successfully: print("App ❌: Cannot start Flask server because data loading failed.")
    elif not openai_configured: print("App ❌: Cannot start Flask server because OpenAI is not configured.")
    else:
        print("App ✅: Data loaded and OpenAI configured. Starting Flask server...")
        app.run(debug=True, port=5000)