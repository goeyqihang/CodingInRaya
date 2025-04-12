# app.py
import os
import openai
from dotenv import load_dotenv

# highlight-start
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
)

import traceback
import re


# Import functions from our modules
from data_utils import load_provided_data
from analysis import (
    get_popular_items_by_frequency,
    get_sales_summary,
    get_popular_cuisines_in_city,
)

# --- Load Environment Variables ---
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

# highlight-start
# --- Secret Key Configuration (No longer strictly required for chat history) ---
# If you have other Flask extensions requiring sessions, you still need to set it.
# For general practice, we keep the check, but it's decoupled from chat history functionality.
flask_secret_key = os.getenv("FLASK_SECRET_KEY")
if not flask_secret_key:
    print(
        "App ⚠️: FLASK_SECRET_KEY not set. Sessions for other features might not work."
    )
    # No longer raising error for chat history, but keep the warning.
else:
    app.secret_key = flask_secret_key
    print("App ✅: Flask Secret Key configured (though not used for chat history).")
# --- End Secret Key Configuration ---
# highlight-end

# --- OpenAI Config ---
openai_configured = False
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    openai.api_key = openai_api_key
    print("App ✅: OpenAI API Key configured successfully.")
    openai_configured = True
except Exception as e:
    print(f"App ❌: Error configuring OpenAI: {e}")
    openai_configured = False


# --- Helper Function ---
def parse_time_period(user_message_lower):
    """Parses user message to determine the desired time period (in English)."""
    if re.search(r"last 3 months|past 90 days", user_message_lower):
        return "last_90_days"
    if re.search(r"last month|past 30 days", user_message_lower):
        return "last_30_days"
    if re.search(r"last week|past 7 days", user_message_lower):
        return "last_7_days"
    # Default to 90 days for analysis/recommendation, 30 for simple queries if unspecified
    if any(
        k in user_message_lower
        for k in [
            "recommend",
            "suggestion",
            "what to sell",
            "startup",
            "new merchant",
            "regional",
            "area",
            "profit",
            "earnings",
            "cuisine",
        ]
    ):
        return "last_90_days"  # Longer period for recommendations
    return "last_30_days"  # Default for general sales/popular items


# --- Page Routes ---
@app.route("/")
def home():
    return render_template("index.html", request=request)


@app.route("/chat")
def chat_page():
    return render_template("chat.html", request=request)


# highlight-start
# --- /api/clear-history route no longer needed ---
# highlight-end

# --- API Route for LLM Interaction (Stateless Backend) ---
print("--- Flask is attempting to define the /api/interact-llm route NOW ---")


@app.route("/api/interact-llm", methods=["POST"])
def handle_llm_interaction():
    global datasets, data_loaded_successfully, openai_configured

    # Check prerequisites
    if not openai_configured:
        return jsonify({"error": "OpenAI API Key not configured."}), 500
    if not data_loaded_successfully or datasets is None:
        return jsonify({"error": "Server data is not available."}), 500

    try:
        req_data = request.get_json()
        # highlight-start
        # Expecting {"history": [...]} from frontend
        if (
            not req_data
            or "history" not in req_data
            or not isinstance(req_data["history"], list)
            or not req_data["history"]
        ):
            return jsonify({"error": "Missing or invalid history in request body"}), 400

        client_history = req_data["history"]

        # Get the latest user message from history for intent recognition
        if not client_history or client_history[-1].get("role") != "user":
            return (
                jsonify({"error": "History is empty or last message not from user"}),
                400,
            )
        user_message = client_history[-1].get("content", "")
        user_message_lower = user_message.lower()
        print(f"\nApp [{request.remote_addr}]: Received latest message: {user_message}")
        print(f"App: Full history received has {len(client_history)} messages.")
        # highlight-end

        # --- Hardcoded IDs (keep for now) ---
        merchant_id_to_query = "3e2b6"
        city_id_to_query = "8"
        city_name_map = {"8": "Subang Jaya"}
        city_name_context = (
            f"{city_name_map.get(city_id_to_query, f'City ID {city_id_to_query}')}"
        )

        data_context = ""
        intent_recognized = False
        response_data = {}

        # --- Keywords (keep unchanged) ---
        popular_item_keywords = ["popular", "hot selling", "best selling", "top items"]
        sales_keywords = [
            "sale",
            "sales",
            "revenue",
            "performance",
            "income",
            "order value",
            "summary",
        ]
        regional_rec_keywords = [
            "recommend",
            "suggestion",
            "what to sell",
            "suitable products",
            "new merchant",
            "startup",
            "regional",
            "area",
            "city",
            "location",
            "cuisine",
        ]
        profit_keywords = [
            "profit",
            "increase profit",
            "improve profit",
            "earnings",
            "make money",
            "bottom line",
            "profitability",
        ]

        # --- Intent Recognition Logic (based on the latest user_message) ---
        # (The if/elif/else logic here uses the extracted user_message and user_message_lower)
        # Intent 1: Profit Improvement
        if any(p in user_message_lower for p in profit_keywords):
            intent_recognized = True
            print(
                f"App: Intent recognized: Profit improvement query for merchant {merchant_id_to_query}"
            )
            time_period_arg = parse_time_period(user_message_lower)
            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
            days_to_query = days_map.get(time_period_arg, 90)

            print(
                f"App: Fetching data for simplified profit analysis (last {days_to_query} days)..."
            )
            sales_summary = get_sales_summary(
                merchant_id_to_query, datasets, time_period_str=time_period_arg
            )
            popular_items = get_popular_items_by_frequency(
                merchant_id_to_query, datasets, days=days_to_query
            )

            context_parts = []
            context_parts.append(
                "User wants advice on increasing profit (note: cost data is unavailable)."
            )
            context_parts.append(
                f"Analysis based on data for merchant {merchant_id_to_query} over the last {days_to_query} days."
            )

            context_parts.append("\n--- Sales Summary ---")
            if isinstance(sales_summary, dict):
                context_parts.append(
                    f"Period: {sales_summary['start_date']} to {sales_summary['end_date']}. Total Sales: RM{sales_summary['total_sales']:,.2f}. Orders: {sales_summary['order_count']}."
                )  # Use RM currency symbol
            elif isinstance(sales_summary, str):
                context_parts.append(f"Could not get sales summary: {sales_summary}.")
            else:
                context_parts.append("No recent sales data found.")

            context_parts.append(
                f"\n--- Popular Items (Top {len(popular_items) if isinstance(popular_items, list) else 'N/A'}) ---"
            )
            if isinstance(popular_items, list) and popular_items:
                items_text = "; ".join(
                    [
                        f"{item['item_name']} ({item['unique_order_count']} unique orders)"
                        for item in popular_items
                    ]
                )
                context_parts.append(f"{items_text}.")
            elif isinstance(popular_items, str):
                context_parts.append(f"Could not get popular items: {popular_items}.")
            else:
                context_parts.append("Could not determine popular items.")

            data_context = "\n".join(context_parts)
            print(f"App: Data Context (Profit Query - Simplified):\n{data_context}")

        # Intent 2: Popular Items
        elif any(p in user_message_lower for p in popular_item_keywords) and not any(
            r in user_message_lower for r in regional_rec_keywords
        ):
            intent_recognized = True
            print(
                f"App: Intent recognized: Popular items query for merchant {merchant_id_to_query}"
            )
            time_period_arg = parse_time_period(user_message_lower)
            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
            days_to_query = days_map.get(time_period_arg, 30)
            popular_items_result = get_popular_items_by_frequency(
                merchant_id_to_query, datasets, days=days_to_query
            )

            if isinstance(popular_items_result, list) and popular_items_result:
                items_text = ", ".join(
                    [
                        f"{item['item_name']} ({item['unique_order_count']} unique orders)"
                        for item in popular_items_result
                    ]
                )
                data_context = f"Data context for merchant {merchant_id_to_query} (popular items last {days_to_query} days by unique orders): Top {len(popular_items_result)} are: {items_text}. "
            elif isinstance(popular_items_result, str):
                data_context = f"Note on data context: Could not get popular items. Reason: {popular_items_result}. "
            else:
                data_context = f"Note on data context: No data for popular items (merchant {merchant_id_to_query}, last {days_to_query} days). "
            print(f"App: Data Context (Popular Items): {data_context}")

        # Intent 3: Sales Performance
        elif any(s in user_message_lower for s in sales_keywords):
            intent_recognized = True
            print(
                f"App: Intent recognized: Sales performance query for merchant {merchant_id_to_query}"
            )
            time_period_arg = parse_time_period(user_message_lower)
            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
            days_to_query = days_map.get(time_period_arg, 30)
            sales_summary_result = get_sales_summary(
                merchant_id_to_query, datasets, time_period_str=time_period_arg
            )

            if isinstance(sales_summary_result, dict):
                start, end = (
                    sales_summary_result["start_date"],
                    sales_summary_result["end_date"],
                )
                sales, count = (
                    sales_summary_result["total_sales"],
                    sales_summary_result["order_count"],
                )
                data_context = f"Data context for merchant {merchant_id_to_query} (Sales Summary {start} to {end}): Total=RM{sales:,.2f}, Orders={count}. "  # Use RM
            elif isinstance(sales_summary_result, str):
                data_context = f"Note on data context: Could not get sales summary. Reason: {sales_summary_result}. "
            else:
                data_context = f"Note on data context: No sales data found (merchant {merchant_id_to_query}, period {time_period_arg}). "
            print(f"App: Data Context (Sales Summary): {data_context}")

        # Intent 4: Regional Cuisine Recommendation
        elif any(r in user_message_lower for r in regional_rec_keywords) and (
            "new merchant" in user_message_lower
            or "what to sell" in user_message_lower
            or "startup" in user_message_lower
            or "recommend" in user_message_lower
            or "suggestion" in user_message_lower
        ):
            intent_recognized = True
            print(
                f"App: Intent recognized: Regional cuisine recommendation for city {city_id_to_query} ({city_name_context})"
            )
            time_period_arg = parse_time_period(user_message_lower)
            days_map = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}
            days_to_query = days_map.get(time_period_arg, 90)
            popular_cuisines_result = get_popular_cuisines_in_city(
                city_id_to_query, datasets, days=days_to_query
            )

            if isinstance(popular_cuisines_result, list) and popular_cuisines_result:
                cuisines_text = ", ".join(popular_cuisines_result)
                data_context = f"Data context: User is asking for recommendations for a new merchant in {city_name_context}. Analysis of recent orders ({days_to_query} days) across merchants shows the top {len(popular_cuisines_result)} most frequent cuisine types are: {cuisines_text}. "
            elif isinstance(popular_cuisines_result, str):
                data_context = f"Note on data context: Could not get popular cuisines data for {city_name_context}. Reason: {popular_cuisines_result}. "
            else:
                data_context = f"Note on data context: Insufficient data for popular cuisine types in {city_name_context} (last {days_to_query} days). "
            print(f"App: Data Context (Regional Cuisines): {data_context}")

        # Fallback / General Query
        else:
            if not intent_recognized:  # Ensure execution if no intent matched
                print("App: Intent: General query or not recognized (Fallback).")
                data_context = ""

        # --- System Prompt (informs LLM history is provided in the API call) ---
        system_prompt = f"""
        You are MEX Assistant, an AI business advisor speaking directly TO a Grab merchant. Your purpose is to help the merchant (you) succeed by turning your data into understandable insights and actionable suggestions. You are based in Malaysia, so use RM for currency when appropriate.

        VERY IMPORTANT: Always address the merchant directly using "you" and "your". Never refer to the merchant as 'the merchant' or by their ID in your response. Keep your tone professional, encouraging, and helpful.

        Analyze the **provided conversation history** (included in the message list) and the specific **Data Context** (provided below, if any, relevant to the *last user message*) to formulate your response to the merchant's *most recent* question. Go beyond just stating the numbers or list; interpret what they imply for your business. Where appropriate, suggest potential actions you could consider based on the data.

        --- Specific instructions for Profit Improvement query ---
        If the user asks how to increase profit:
        1. Start by clearly stating that direct profit calculation isn't possible due to missing cost data, so the advice focuses on improving potential profitability through revenue and efficiency.
        2. Briefly summarize your recent sales performance using the figures from the 'Sales Summary' section in the context (use RM).
        3. Discuss your popular items (using names and **unique order counts** from the 'Popular Items' section). Suggest specific ways you could leverage these (e.g., 'Consider promoting [Popular Item Name] which was in [N] **unique orders**...', potential bundling, ensuring stock).
        4. Synthesize these points: Explain how focusing on popular items might boost revenue.
        5. Conclude with general advice relevant to F&B in places like Malaysia: reviewing pricing (RM) against competitors, menu diversity, considering local tastes, operational efficiency (delivery times, packaging), and potentially exploring promotions on the Grab platform.
        --- End of Profit Improvement instructions ---

        If you identify as a new merchant asking for advice on what to sell in {city_name_context}, use the popular cuisine data (if provided in the 'Regional Cuisine' context section) to suggest focusing on those categories, while also advising you to conduct deeper local market research (competitors, target audience preferences, rental costs) and consider differentiation (unique selling points).

        If no specific data context is available ('Data Context:' below is empty) or the context is just a note ('Note on data context: ...'), address the *last user question* directly based on the provided conversation history and general business knowledge relevant to Malaysian F&B merchants.
        If the context notes an error or lack of data ('Note on data context: Could not get...'), clearly communicate this limitation to you first before attempting a general answer based on conversation history or general knowledge.

        Be clear, concise, and focus on providing practical value to the merchant (you). Respond in English. Use Markdown for formatting.

        Data Context (relevant to the last user message):
        {data_context}
        """
        # --- End of System Prompt ---

        # highlight-start
        # Construct message list for OpenAI (System Prompt + History from frontend)
        messages = [{"role": "system", "content": system_prompt.strip()}]
        # Assuming client_history already includes the latest user message
        messages.extend(client_history)

        print(
            f"App: --- Sending Messages to OpenAI (Using history from client, {len(client_history)} messages) ---"
        )

        # --- Call OpenAI API ---
        try:
            completion = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                temperature=0.6,  # Adjusted temperature parameter slightly
            )
            llm_reply = completion.choices[0].message.content.strip()
            print("App: LLM Reply received successfully.")
            response_data["reply"] = llm_reply

        except Exception as e:
            print(f"App ❌: OpenAI API call failed: {e}")
            traceback.print_exc()
            # Keep Chinese error message for user-facing errors if preferred
            response_data["reply"] = (
                "抱歉，我在尝试从 AI 获取回应时遇到问题。这可能是暂时性的，请稍后再试。如果问题持续存在，请联系技术支持。"
            )

        # --- Return Response ---
        # Only return AI reply, frontend manages history state
        return jsonify(response_data)

    # --- Global Error Handling for the API Route ---
    except Exception as e:
        print(f"App ❌: An unexpected error occurred in /api/interact-llm: {e}")
        traceback.print_exc()
        # Keep Chinese error message for user-facing errors if preferred
        return jsonify({"error": "处理您的请求时服务器发生意外错误。"}), 500


# --- Flask run ---
if __name__ == "__main__":
    print("\n--- Starting Application ---")
    # Perform checks before starting the server
    if not data_loaded_successfully:
        # Log message in English
        print("App ❌: Cannot start Flask server because initial data loading failed.")
    elif not openai_configured:
        # Log message in English
        print(
            "App ❌: Cannot start Flask server because OpenAI API Key is not configured."
        )
    # No longer enforcing secret_key check as startup condition (as it's not used for chat history)
    else:
        # Log message in English
        print("App ✅: Pre-flight checks passed (Data and OpenAI configured).")
        # highlight-start
        # Log message in English
        print("App ℹ️: Conversation history is managed by frontend (stateless backend).")
        # highlight-end
        # Log message in English
        print("App ▶️: Starting Flask server... Access at http://127.0.0.1:5000")
        # debug=True for development (auto-reloads), use debug=False for production
        # host='0.0.0.0' makes the server accessible on your network (use with caution)
        app.run(debug=True, port=5000)

    # Log message in English
    print("--- Application Closed ---")
