# tools/bq_query.py
# Executes natural-language-driven queries against BigQuery sales tables.

from google.cloud import bigquery
from sales_agent.config import GCP_PROJECT_ID, BQ_DATASET, BQ_SALES_TABLE


# Initialise BigQuery client once at module load.
# Authentication uses Application Default Credentials (ADC).
# Run `gcloud auth application-default login` locally to set this up.
_bq_client = bigquery.Client(project=GCP_PROJECT_ID)


def query_sales_data(
    sql_query: str,
    max_rows: int = 100,
) -> dict:
    """
    Executes a SQL query against the BigQuery sales dataset and returns results.

    Use this tool whenever the user asks about sales figures, revenue, orders,
    customer counts, regional performance, or any other data stored in BigQuery.

    You (the agent) are responsible for writing the SQL query based on the
    user's question. Always use fully-qualified table names in the format:
    `{project}.{dataset}.{table}`.

    Available tables:
    - sales_transactions : order_id, customer_id, region, product_id,
                           quantity, unit_price, order_date, status
    - customers          : customer_id, name, email, segment, signup_date
    - products           : product_id, name, category, cost_price

    Args:
        sql_query: A valid BigQuery Standard SQL query string.
        max_rows:  Maximum number of rows to return (default 100, max 500).

    Returns:
        A dict with keys:
          - status  : "success" or "error"
          - rows    : list of dicts (column -> value) if successful
          - row_count : number of rows returned
          - columns : list of column names
          - error   : error message string if status is "error"

    Example sql_query:
        SELECT region,
               SUM(quantity * unit_price) AS total_revenue
        FROM `my-project.sales_data.sales_transactions`
        WHERE DATE(order_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        GROUP BY region
        ORDER BY total_revenue DESC
    """
    if max_rows > 500:
        max_rows = 500

    try:
        query_job = _bq_client.query(sql_query)
        results = query_job.result(max_results=max_rows)

        columns = [field.name for field in results.schema]
        rows = [dict(zip(columns, row.values())) for row in results]

        return {
            "status": "success",
            "rows": rows,
            "row_count": len(rows),
            "columns": columns,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "rows": [],
            "row_count": 0,
            "columns": [],
        }


def get_table_schema(table_name: str) -> dict:
    """
    Returns the schema (column names and types) for a given BigQuery table.

    Use this tool when you are unsure which columns exist before writing a
    SQL query. Valid table_name values: sales_transactions, customers, products.

    Args:
        table_name: Short table name (without project/dataset prefix).

    Returns:
        A dict with keys:
          - status  : "success" or "error"
          - schema  : list of dicts with 'name', 'type', 'description' keys
          - error   : error message if status is "error"
    """
    full_table_id = f"{GCP_PROJECT_ID}.{BQ_DATASET}.{table_name}"

    try:
        table = _bq_client.get_table(full_table_id)
        schema = [
            {
                "name": field.name,
                "type": field.field_type,
                "description": field.description or "",
            }
            for field in table.schema
        ]
        return {"status": "success", "schema": schema}

    except Exception as e:
        return {"status": "error", "error": str(e), "schema": []}
