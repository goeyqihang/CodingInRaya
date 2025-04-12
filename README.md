# MEX Assistant - Grab UMHackathon 2025 Prototype

## Project Goal

This project is a functional prototype developed for the **UMHackathon 2025**, addressing **Domain 3: Economic Empowerment through AI**. 

The goal is to build **MEX Assistant**, an AI-powered chat assistant designed to empower Grab's merchant-partners (MEX) by providing actionable insights and guidance derived from their own business data. This prototype focuses on demonstrating core capabilities via a web-based chat interface.

## Features Implemented

* **Chat Interface:** A web interface (`/chat`) allowing merchants to interact with the AI assistant.
* **Data Loading & Preprocessing:** Loads and cleans data from provided CSV files (`merchant`, `transaction_data`, `transaction_items`, `items`, `keywords`).
* **Intent Recognition:** Basic intent recognition to understand user queries related to:
    * Sales Performance Summary
    * Popular Items (based on unique order count)
    * Regional Cuisine Popularity (for new merchant recommendations)
    * Profit Improvement Suggestions
* **Data Analysis:**
    * Calculates sales summaries (total value, order count) for specific time periods (`get_sales_summary`).
    * Identifies top 5 popular items based on unique order counts for specific time periods (`get_popular_items_by_frequency`).
    * Analyzes popular cuisine types within a specific city based on aggregate order frequency (`get_popular_cuisines_in_city`).
    * *Note: Profit analysis currently synthesizes sales and popular item data, acknowledging the lack of cost data.*
* **AI Interaction:**
    * Uses the OpenAI API (configured for GPT-4-Turbo as per discussion) to generate natural language responses.
    * Provides data context to the AI based on recognized intent.
    * Uses tailored system prompts to guide the AI's persona and response generation (including addressing the user in the second person).
* **Basic Dashboard UI:** Includes a static dashboard layout (`/`) with hardcoded sample chart images for visual context (requires running `generate_sample_charts.py`).

## Technology Stack

* **Backend:** Python 3.x, Flask
* **Data Handling:** Pandas, NumPy
* **AI Model:** OpenAI API (GPT-4-Turbo or configurable via environment variable)
* **Frontend:** HTML (Jinja2 Templating), CSS, Vanilla JavaScript
* **Environment:** python-dotenv
* **Chart Generation (Static Samples):** Matplotlib, Seaborn
* **Markdown Rendering (Frontend):** marked.js (via CDN)

## Project Structure

```text
CODINGINRAYA/
├── app.py                 # Main Flask application, routes, API logic
├── analysis.py            # Data analysis functions
├── data_utils.py          # Data loading and preprocessing functions
├── generate_sample_charts.py # Script to create placeholder chart images
├── data/                    # Directory for input CSV files
│   ├── items.csv
│   ├── keywords.csv
│   ├── merchant.csv
│   ├── transaction_data.csv
│   └── transaction_items.csv
├── static/                  # Static assets
│   ├── css/style.css
│   ├── images/            # Place generated/downloaded images here
│   │   └── grab-logo.png
│   │   └── sample_*.png
│   └── js/chat_script.js
├── templates/               # HTML templates
│   ├── base.html
│   ├── chat.html
│   └── index.html
├── venv/                    # Python virtual environment (recommended)
├── .env                     # Stores API keys (MUST be created)
├── .gitignore
├── requirements.txt         # Python dependencies (MUST be created)
└── README.md                # This file
```
## Data

The application requires the following CSV files to be placed in the `data/` directory:

* `merchant.csv`
* `transaction_data.csv`
* `transaction_items.csv`
* `items.csv`
* `keywords.csv`

Ensure these files exist and contain the expected columns for the analysis functions to work correctly (e.g., `order_value`, `order_time`, `city_id`, `item_id`, `cuisine_tag`).

## Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd CODINGINRAYA
    ```
2.  **Create Virtual Environment:** (Recommended)
    ```bash
    python -m venv venv
    ```
3.  **Activate Virtual Environment:**
    * Windows: `venv\Scripts\activate`
    * macOS/Linux: `source venv/bin/activate`
4.  **Install Dependencies:** Create a `requirements.txt` file (see content in previous response or generate using `pip freeze`) in the root directory and run:
    ```bash
    pip install -r requirements.txt
    ```
    *(Required libraries: flask, pandas, python-dotenv, openai, numpy, matplotlib, seaborn)*
5.  **Set Up Environment Variables:** Create a file named `.env` in the project root directory and add your OpenAI API key:
    ```dotenv
    OPENAI_API_KEY=sk-YourSecretOpenAiApiKeyGoesHere
    ```
6.  **Add Data:** Place the required CSV files into the `data/` directory.
7.  **(Optional) Generate Sample Chart Images:** To populate the static dashboard (`/`) with visual placeholders, run the generation script (ensure `static/images/` exists):
    ```bash
    python generate_sample_charts.py
    ```

## Running the Application

1.  Make sure your virtual environment is activated.
2.  Run the Flask development server from the project root directory:
    ```bash
    python -m flask --debug run
    ```
    (Or `python app.py` if using `app.run()` directly)
3.  Open your web browser and navigate to `http://127.0.0.1:5000/chat` to access the MEX Assistant chat interface.
4.  Navigate to `http://127.0.0.1:5000/` to view the static Insights dashboard (if chart images were generated).

## Configuration Notes

* The specific merchant ID (`merchant_id_to_query`) and city ID (`city_id_to_query`) used for certain analyses are currently hardcoded in `app.py`. Modify these directly in the code if you need to analyze different default entities. In a production scenario, this would typically come from user authentication or selection.
* Ensure the OpenAI model name (`gpt-4-turbo` used in the last version) in `app.py` matches a model accessible by your API key.

## Future Improvements (Ideas)

* Implement analysis for specific item performance (revenue, trends).
* Add sales trend analysis (comparison between periods).
* Integrate cost data for actual profit calculation.
* Develop more robust intent recognition (e.g., using embeddings, LLM function calling).
* Implement user authentication to fetch data for the logged-in merchant dynamically.
* Explore dynamic chart generation using JavaScript libraries based on data sent from the backend for the Insights page or even within the chat.