# tests/test_bq_query.py
# Unit tests for the BigQuery query tool.
# These use mocking so you don't need a live BQ connection to run them.

from unittest.mock import MagicMock, patch

from sales_agent.tools.bq_query import get_table_schema, query_sales_data


def _make_mock_row(data: dict):
    """Helper — creates a mock BigQuery row that behaves like the real one."""
    row = MagicMock()
    row.values.return_value = list(data.values())
    return row


def _make_mock_field(name: str):
    """Helper — creates a mock BigQuery schema field with a real name value."""
    field = MagicMock()
    field.name = name
    return field


@patch("sales_agent.tools.bq_query._bq_client")
def test_query_sales_data_success(mock_client):
    """query_sales_data returns rows and correct column names on success."""
    mock_row = _make_mock_row({"region": "North", "total_revenue": 50000})
    mock_results = MagicMock()
    mock_results.schema = [
        _make_mock_field("region"),
        _make_mock_field("total_revenue"),
    ]
    mock_results.__iter__ = MagicMock(return_value=iter([mock_row]))
    mock_client.query.return_value.result.return_value = mock_results

    result = query_sales_data("SELECT region, SUM(revenue) FROM sales GROUP BY region")

    assert result["status"] == "success"
    assert result["row_count"] == 1
    assert "region" in result["columns"]


@patch("sales_agent.tools.bq_query._bq_client")
def test_query_sales_data_error(mock_client):
    """query_sales_data returns error dict when BigQuery raises an exception."""
    mock_client.query.side_effect = Exception("Table not found")

    result = query_sales_data("SELECT * FROM nonexistent_table")

    assert result["status"] == "error"
    assert "Table not found" in result["error"]
    assert result["rows"] == []


def test_query_sales_data_max_rows_capped():
    """max_rows above 500 should be silently capped at 500."""
    with patch("sales_agent.tools.bq_query._bq_client") as mock_client:
        mock_results = MagicMock()
        mock_results.schema = []
        mock_results.__iter__ = MagicMock(return_value=iter([]))
        mock_client.query.return_value.result.return_value = mock_results

        query_sales_data("SELECT 1", max_rows=9999)
        mock_client.query.return_value.result.assert_called_with(max_results=500)
