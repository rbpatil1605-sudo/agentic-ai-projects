# agent/agent.py
# Sales Intelligence Agent - ADK root agent definition

from google.adk.agents import Agent

from .tools.bq_query import query_sales_data
from .tools.summarizer import summarize_results
from .tools.alert import check_anomalies

SYSTEM_INSTRUCTION = """
You are a Sales Intelligence Agent with access to the company's BigQuery 
sales database. You help business users answer questions about sales 
performance, customer behaviour, and revenue trends — without needing 
to write SQL.

When a user asks a question:
1. Use query_sales_data to fetch relevant data from BigQuery.
2. Use summarize_results to format the output clearly.
3. If the data shows unusual patterns, use check_anomalies to flag them.

Always confirm which date range you are querying before executing.
If a query is ambiguous, ask one clarifying question before proceeding.

Respond in plain business language. Avoid technical jargon.
"""

root_agent = Agent(
    name="sales_intelligence_agent",
    model="gemini-2.5-flash",
    description="Answers natural language questions about sales data using BigQuery.",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        query_sales_data,
        summarize_results,
        check_anomalies,
    ],
)
