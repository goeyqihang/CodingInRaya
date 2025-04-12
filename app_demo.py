# app_demo.py (Sequential Hardcoded Demo Version - CORRECTED LOGIC)

import os
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import traceback
import re

# Import functions (might be unused, keep for structure)
from data_utils import load_provided_data

# --- Load Environment Variables ---
load_dotenv()

# --- Initialize Data (Keep for structure) ---
datasets = None
data_loaded_successfully = False
try:
    print("App_Demo: Attempting to load data via data_utils...")
    datasets = load_provided_data()
    if datasets:
        data_loaded_successfully = True
        print("App_Demo ✅: Data loaded successfully via data_utils.")
    else:
        data_loaded_successfully = False
        print("App_Demo ❌: Data loading failed.")
except Exception as e:
    print(f"App_Demo ❌: Critical error during initial data load call: {e}")
    traceback.print_exc()
    data_loaded_successfully = False
    datasets = None

# --- Flask App Setup ---
app = Flask(__name__)

# --- Secret Key Configuration (Optional but good practice) ---
flask_secret_key = os.getenv("FLASK_SECRET_KEY")
if not flask_secret_key:
    print(
        "App_Demo ⚠️: FLASK_SECRET_KEY not set. Sessions for other features might not work."
    )
else:
    app.secret_key = flask_secret_key
    print(
        "App_Demo ✅: Flask Secret Key configured (though not used for chat history)."
    )

# --- OpenAI Config (Keep for structure) ---
openai_configured = False
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    openai.api_key = openai_api_key
    print("App_Demo ✅: OpenAI API Key configured successfully.")
    openai_configured = True
except Exception as e:
    print(f"App_Demo ❌: Error configuring OpenAI: {e}")
    openai_configured = False


# --- Helper Function (Keep for structure) ---
def parse_time_period(user_message_lower):
    if re.search(r"last 3 months|past 90 days", user_message_lower):
        return "last_90_days"
    if re.search(r"last month|past 30 days", user_message_lower):
        return "last_30_days"
    if re.search(r"last week|past 7 days", user_message_lower):
        return "last_7_days"
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
        return "last_90_days"
    return "last_30_days"


# --- Page Routes (Keep) ---
@app.route("/")
def home():
    return render_template("index.html", request=request)


@app.route("/chat")
def chat_page():
    return render_template("chat.html", request=request)


# --- API Route for LLM Interaction (DEMO VERSION - Sequential Responses - CORRECTED) ---
print(
    "--- Flask (Demo Version - Sequential Corrected) is attempting to define the /api/interact-llm route NOW ---"
)


@app.route("/api/interact-llm", methods=["POST"])
def handle_llm_interaction():
    # Keep prerequisite checks
    global datasets, data_loaded_successfully, openai_configured
    if not openai_configured:
        return jsonify({"error": "OpenAI API Key not configured."}), 500
    if not data_loaded_successfully or datasets is None:
        return jsonify({"error": "Server data is not available."}), 500

    try:
        req_data = request.get_json()
        # Expecting {"history": [...]} from frontend
        if (
            not req_data
            or "history" not in req_data
            or not isinstance(req_data["history"], list)
            or not req_data["history"]
        ):
            return jsonify({"error": "Missing or invalid history in request body"}), 400

        client_history = req_data["history"]
        # --- MODIFICATION START: Calculate user message count ---
        user_message_count = sum(
            1 for msg in client_history if msg.get("role") == "user"
        )
        print(
            f"\nApp_Demo [{request.remote_addr}]: Received history with {user_message_count} user message(s)."
        )
        # --- MODIFICATION END ---

        response_data = {}
        reply_list = None  # Use a list to store replies

        # Define fallback message list
        fallback_replies = [
            (
                "**(Demo Mode)** That concludes the planned demonstration sequence."
                " Thank you for exploring the MEX Assistant prototype!"
            )
        ]

        # --- SEQUENTIAL DEMO LOGIC based on USER MESSAGE COUNT ---
        # Determine response based on the number of user messages in history

        if user_message_count == 1:  # First user message received
            print("App_Demo: User message count 1 -> Returning Demo Response 1.")
            # TODO: Replace with your list of replies for the FIRST user interaction
            reply_list = [
                """
                Good afternoon, QuickBites Cafe! I've looked at your sales data for this week (Monday to Friday). In summary:
                Total orders increased by 5% compared to last week, and the Average Order Value (AOV) remained stable around RM22.

                """,
                """
                To see the daily performance more clearly, would you like me to show a graph of the daily sales trend for this week?
                """,
            ]

        elif user_message_count == 2:  # Second user message received
            print(
                "App_Demo: User message count 2 -> Returning Demo Response 2 (potentially multiple)."
            )
            # TODO: Replace with your list of replies for the SECOND user interaction
            # Example with two replies and image:
            reply_list = [
                """
                Alright. Here is the line graph showing your total daily orders throughout this week.
                ![Popular Items Pie Chart](/static/images/daily_orders_graph.png)
                """,
                """
                From this graph, we can see that Friday had the highest sales, but there was a slight dip on Thursday compared to the other 
                days.
                """,
                """
                Additionally, I have another interesting observation. Your "Spicy Chicken Sandwich" item received a lot of attention - keywords 
                related to this item were searched and viewed 600 times this week. However, it was only ordered 30 times. It seems many 
                people view it, but not many proceed to buy.
                """,
            ]

        elif user_message_count == 3:  # Third user message received
            print("App_Demo: User message count 3 -> Returning Demo Response 3.")
            # TODO: Replace with your list of replies for the THIRD user interaction
            reply_list = [
                """
                Price might be one factor. Other factors could be that the item's picture or description is less appealing.
                Considering that Thursday's sales were a bit slower, and this "Spicy Chicken Sandwich" has potential but isn't 
                converting well, how about trying a special promotion for this sandwich specifically on Thursdays? For example, 
                an RM3 discount or a combo set with a drink? This could help boost Thursday's sales and also increase the sandwich's 
                conversion rate. Would you like help setting up the promotion?
                """
            ]

        elif user_message_count == 4:
            print("App_Demo: User message count 4 -> Returning Demo Response 4.")
            reply_list = [
                """ 
                Done! The RM3 discount promotion for the "Spicy Chicken Sandwich" this Thursday is now active. 👍 Hopefully, 
                it helps increase your sales! Is there anything else I can help you with?
                """
            ]
        elif user_message_count == 5:
            print("App_Demo: User message count 5 -> Returning Demo Response 5.")
            reply_list = [
                """ 
                Baik Tuan, Tuan nak sahkan bila promosi tu bermula.
                """,
                """
                Promosi diskaun RM3 ni bermula hari Khamis ini (iaitu esok) sebaik sahaja kedai Tuan dibuka, dan berlangsung sehingga 
                akhir waktu operasi pada hari tersebut.
                """,
            ]

        # --- Fallback / End of Demo ---
        if reply_list is None:
            # This triggers if user_message_count exceeds the defined steps
            print(
                "App_Demo: User message count doesn't match a defined demo step. Returning fallback."
            )
            reply_list = fallback_replies  # Use the fallback list

        # --- Package response ---
        # Always return a list under the key 'replies'
        response_data["replies"] = [
            reply.strip() for reply in reply_list
        ]  # Ensure each reply is stripped
        return jsonify(response_data)

        # --- Live LLM Call section is bypassed ---

    except Exception as e:
        print(f"App_Demo ❌: An unexpected error occurred in /api/interact-llm: {e}")
        traceback.print_exc()
        return jsonify({"error": "处理您的请求时服务器发生意外错误。"}), 500


# --- Flask run block for app_demo.py ---
if __name__ == "__main__":
    print(
        "\n--- Starting SEQUENTIAL DEMO Application (app_demo.py - Corrected Logic) ---"
    )  # Indicate corrected logic
    if not data_loaded_successfully:
        print("App_Demo ⚠️: Data loading failed, proceeding.")
    if not openai_configured:
        print("App_Demo ⚠️: OpenAI Key not configured, proceeding.")

    print("App_Demo ✅: Checks passed (or warnings issued).")
    print(
        "App_Demo ℹ️: Running in SEQUENTIAL HARDCODED response mode (using user message count)."
    )  # Indicate mode
    print("App_Demo ▶️: Starting Flask server... Access at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)

    print("--- SEQUENTIAL DEMO Application Closed ---")
