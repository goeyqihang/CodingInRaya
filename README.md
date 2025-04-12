# MEX Assistant - AI Business Advisor for Grab Merchants (UMHackathon 2025 Prototype)

   **[➡️ View Presentation Slides](https://docs.google.com/presentation/d/1PPH9yx-9Dnsjoy-uEY1-2SwvkmQAaklgi3BXsHk7ebg/edit?usp=sharing)** 

## Description

MEX Assistant is an AI-powered chatbot designed as a prototype for the UMHackathon 2025. It aims to provide business insights and actionable suggestions to Grab merchants (MEX) by analyzing their sales, item, and transaction data. The assistant offers insights on sales performance, popular items, regional cuisine trends (for new merchants), and potential strategies for improvement.

This repository includes:
1.  A **Live Version** (`app.py`) that utilizes the OpenAI API (GPT-4-Turbo) to generate dynamic responses based on data context and conversation history.
2.  A **Demo Version** (`app_demo.py`) that provides a hardcoded, sequential walkthrough of key features with predefined responses and images, suitable for predictable demonstrations without API calls.

The current implementation features a Flask backend, data analysis using Pandas, and a web interface built with HTML, CSS, and vanilla JavaScript. Chat history for both versions is managed client-side within the browser's memory for the duration of the session.

## Features

* **Data Analysis:** Performs analyses on provided CSV data for:
    * Sales Summary (Total Sales, Order Count) over specified periods.
    * Popular Items (Top 5 based on unique order counts).
    * Regional Cuisine Popularity (Top 5 cuisine tags in a city based on unique orders).
    * Low Performing Items (Bottom 5 based on unique order counts).
* **Chat Interface:** Web-based chat UI (`/chat` page) allowing users to interact with the assistant.
* **Intent Recognition (Live Mode):** Basic keyword-based intent recognition to fetch relevant data context (Sales, Popular Items, Regional Trends, Profit Advice) for the LLM.
* **Dynamic AI Responses (Live Mode):** Uses OpenAI's GPT-4-Turbo, guided by a system prompt and data context, to generate tailored advice.
* **Hardcoded Demo Sequence (Demo Mode):** Provides a reliable, step-by-step demonstration of features using predefined responses, including multi-part replies and image display.
* **Client-Side History:** Manages conversation history in the browser using JavaScript memory (cleared on page refresh/close).
* **Markdown & Image Support:** Renders AI responses formatted with Markdown (using Marked.js) and displays images embedded in demo replies.
* **Basic Dashboard UI:** Includes a static dashboard layout (`/` page) resembling the Grab Merchant interface structure.

## Technology Stack

* **Backend:** Python 3.x, Flask
* **Frontend:** HTML5, CSS3, JavaScript (ES6+)
* **Data Handling:** Pandas, NumPy
* **AI Model (Live Mode):** OpenAI API (specifically `gpt-4-turbo`)
* **Libraries:**
    * `openai`: For interacting with the OpenAI API.
    * `python-dotenv`: For managing environment variables.
    * `Flask`: Web framework.
    * `Pandas`: Data manipulation and analysis.
    * `Marked.js`: (CDN) For rendering Markdown on the frontend.
    * `Font Awesome`: (CDN) For icons.
* **Key Python Libraries:** (Based on provided list - ensure `requirements.txt` is accurate)
    * `Flask==3.1.0`
    * `pandas==2.2.3`
    * `openai==1.72.0`
    * `python-dotenv==1.1.0`
    * `numpy==2.2.4`
    * ... and others (refer to your generated `requirements.txt`)

## Project Structure

```text
CODINGINRAYA/
├── app.py                 # Main application (Live AI)
├── app_demo.py            # Demo application (Hardcoded Sequence)
├── analysis.py            # Data analysis functions
├── data_utils.py          # Data loading and preprocessing functions
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API keys, Secret Key) - !! DO NOT COMMIT !!
├── .gitignore             # Files/folders to ignore in git
├── data/                  # CSV data files (needs to be populated)
│   ├── merchant.csv
│   ├── transaction_data.csv
│   ├── transaction_items.csv
│   ├── items.csv
│   └── keywords.csv         # (Assuming this is also needed based on data_utils)
├── static/                # Static assets
│   ├── css/
│   │   └── style.css      # Main stylesheet
│   ├── js/
│   │   └── chat_script.js # Frontend chat logic
│   └── images/            # Demo images (e.g., daily_orders_graph.png, grab-logo.png)
│       └── ...
└── templates/             # HTML templates
├── base.html          # Base template with sidebar/layout
├── index.html         # Static dashboard page
└── chat.html          # Chat interface page
```

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-folder>
    ```
2.  **Create and activate a virtual environment:** (Recommended)
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensure `requirements.txt` accurately reflects all needed packages using `pip freeze > requirements.txt` in your activated virtual environment).*
4.  **Create `.env` file:** Create a file named `.env` in the project root directory. Add your OpenAI API key and generate a Flask secret key:
    ```dotenv
    OPENAI_API_KEY=sk-YourActualOpenAIKeyHere
    FLASK_SECRET_KEY=YourGeneratedStrongSecretKeyHere
    ```
    * Generate a strong `FLASK_SECRET_KEY` in your terminal using:
        ```bash
        python -c "import secrets; print(secrets.token_hex(24))"
        ```
5.  **Add Data Files:** Create a `data/` directory in the project root. Place the required CSV data files (`merchant.csv`, `transaction_data.csv`, `transaction_items.csv`, `items.csv`, `keywords.csv`) inside it.
6.  **Add Images:** Create a `static/images/` directory. Place any images used (like the Grab logo for the sidebar and any charts/graphs referenced in `app_demo.py` or `index.html`) inside it. Ensure filenames match the paths used in the code (e.g., `daily_orders_graph.png`).

## Running the Application

You can run either the live version (connecting to OpenAI) or the hardcoded demo version. Ensure only one is running at a time on the default port (5000) to avoid conflicts.

**1. Running the Live Version (`app.py`)**

* Connects to the OpenAI API for responses. Requires a valid `OPENAI_API_KEY`.
* Chat history is managed in the browser's memory for the current session (cleared on refresh).
* Command:
    ```bash
    python app.py
    ```
    or using Flask CLI:
    ```bash
    flask --app app run --debug
    ```

**2. Running the Demo Version (`app_demo.py`)**

* Uses hardcoded responses based on user message count. Does **not** call the OpenAI API.
* Ideal for predictable demonstrations.
* Chat history is managed in the browser's memory for the current session (cleared on refresh).
* Command:
    ```bash
    python app_demo.py
    ```
    or using Flask CLI:
    ```bash
    flask --app app_demo run --debug
    ```

**Accessing the Application:**

Once the server is running (either version), open your web browser and navigate to:
`http://127.0.0.1:5000`

* Navigate to the **MEX Assistant** link in the sidebar (or directly to `/chat`) to use the chat interface.

## Demo Sequence (`app_demo.py`)

The hardcoded demo version (`app_demo.py`) follows this specific interaction flow based on the count of user messages sent during the current browser session:

1.  **User sends 1st message:** AI replies with a welcome and a weekly sales summary (5% order increase, stable AOV ~RM22), and asks about showing a daily graph (2 replies).
2.  **User sends 2nd message:** AI replies showing the daily orders line graph (`daily_orders_graph.png`), comments on sales trends (e.g., Friday high, Thursday dip), and provides an observation about a specific item's view vs. order conversion rate (e.g., Spicy Chicken Sandwich) (3 replies).
3.  **User sends 3rd message:** AI replies suggesting reasons for the low conversion and proposes a specific promotion (e.g., Thursday discount for the sandwich), asking if the user wants help setting it up (1 reply).
4.  **User sends 4th message:** AI replies confirming the RM3 discount promotion for Thursday is now active and asks if there's anything else (1 reply).
5.  **User sends 5th message:** AI replies confirming the promotion start details (Thursday, from opening to closing) in Malay (2 replies).
6.  **Subsequent messages:** AI returns a fallback message indicating the end of the planned demo sequence.

*Note: Ensure the image file paths referenced in `app_demo.py` (e.g., `/static/images/daily_orders_graph.png`) exist and contain the appropriate demo images.*

## Data

The application requires the following CSV files placed in the `data/` directory:

* `merchant.csv`
* `transaction_data.csv`
* `transaction_items.csv`
* `items.csv`
* `keywords.csv` (based on `data_utils.py`)

The quality and format of the data in these files directly impact the analysis results generated by `analysis.py` (in the live version). `data_utils.py` performs essential preprocessing.

## Notes / Known Issues

* **Hardcoded IDs:** The current implementation uses hardcoded `merchant_id` ('3e2b6') and `city_id` ('8' - Subang Jaya) in the analysis calls. This should be made dynamic for real-world use.
* **Client-Side History:** History is lost on page refresh or closing the tab. This is suitable for demos where a fresh start is desired on reload but not for persistent conversations. History length is also limited client-side.
* **Demo Data:** The hardcoded demo responses use specific example data values and item names (e.g., RM 5,250.50, Nasi Lemak Special). Ensure these align with the story you want to tell in the demo.
* **Error Handling:** Basic error handling is implemented, but could be enhanced.
* **Security:** API keys and the Flask secret key should be kept confidential (use `.env` and add it to `.gitignore`). Input sanitization is minimal as the primary interaction driver is the hardcoded sequence or trusted API calls.
