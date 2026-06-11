# config/settings.py
# Central config — all GCP and BigQuery references live here.
# Values are loaded from the .env file. Never hardcode credentials here.

import os
from dotenv import load_dotenv

load_dotenv()  # loads .env from the project root

# --- Google Cloud ---
GCP_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "gcai-may-26")
# --- BigQuery ---
BQ_DATASET     = os.getenv("BQ_DATASET", "sales_data")
BQ_SALES_TABLE = os.getenv("BQ_SALES_TABLE", "sales_transactions")

# --- Agent model ---
GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
