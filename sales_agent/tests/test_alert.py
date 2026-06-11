# tests/test_alert.py
# Unit tests for the anomaly detection tool — no GCP connection needed.

from sales_agent.tools.alert import check_anomalies


def test_no_anomalies_in_normal_data():
    rows = [
        {"region": "North", "revenue": 10000},
        {"region": "South", "revenue": 11000},
        {"region": "East",  "revenue": 9500},
        {"region": "West",  "revenue": 10500},
    ]
    result = check_anomalies(rows, metric_column="revenue")
    assert result["status"] == "success"
    assert result["anomalies_found"] is False
    assert result["flagged_rows"] == []


def test_detects_drop_anomaly():
    rows = [
        {"region": "North", "revenue": 10000},
        {"region": "South", "revenue": 10000},
        {"region": "East",  "revenue": 10000},
        {"region": "West",  "revenue": 1000},   # 90% below mean → should flag
    ]
    result = check_anomalies(rows, metric_column="revenue", threshold_pct_drop=20.0)
    assert result["anomalies_found"] is True
    flagged_regions = [r["region"] for r in result["flagged_rows"]]
    assert "West" in flagged_regions


def test_empty_rows():
    result = check_anomalies([], metric_column="revenue")
    assert result["status"] == "success"
    assert result["anomalies_found"] is False


def test_missing_column():
    rows = [{"region": "North", "revenue": 5000}]
    result = check_anomalies(rows, metric_column="nonexistent_column")
    assert result["status"] == "error"
