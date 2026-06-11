"""Config package exports for the Sales Intelligence Agent."""

from .settings import BQ_DATASET, BQ_SALES_TABLE, GEMINI_MODEL, GCP_PROJECT_ID

__all__ = [
    "BQ_DATASET",
    "BQ_SALES_TABLE",
    "GEMINI_MODEL",
    "GCP_PROJECT_ID",
]
