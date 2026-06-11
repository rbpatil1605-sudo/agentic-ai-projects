# Sales Intelligence Agent

A natural language agent built with Google ADK that answers business questions
about sales data stored in BigQuery.

## What it does

- Accepts plain English questions like *"Which regions underperformed last month?"*
- Writes and executes BigQuery SQL automatically
- Formats results as tables or bullet summaries
- Flags anomalies and unusual patterns proactively

## Setup

### 1. Install dependencies

```powershell
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
```

### 2. Configure credentials

```powershell
copy .env.example .env
# Edit .env and fill in your GCP project ID and credentials path
```

Authenticate with GCP:
```powershell
gcloud auth application-default login
```

### 3. Run locally with ADK web

```powershell
cd sales-agent
adk web
```

Then open http://localhost:8000 in your browser.

## Project structure

```
sales-agent/
  agent/          ← ADK root_agent definition
  tools/          ← one file per tool (BQ query, summarizer, alerts)
  config/         ← GCP project settings loaded from .env
  tests/          ← unit tests
```

## Example questions to ask

- "Show me total revenue by region for the last 30 days"
- "Which customers haven't placed an order in 90 days?"
- "Are there any products with unusually low sales this week?"
- "Compare this month's revenue to last month"
