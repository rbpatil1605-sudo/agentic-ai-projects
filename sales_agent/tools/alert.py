# tools/alert.py
# Detects anomalies and threshold breaches in sales query results.


def check_anomalies(
    rows: list,
    metric_column: str,
    threshold_pct_drop: float = 20.0,
    threshold_pct_spike: float = 50.0,
) -> dict:
    """
    Scans a set of rows for unusual values — large drops or spikes in a
    numeric metric column — and returns flagged items.

    Use this tool after query_sales_data when the user asks about performance
    issues, anomalies, underperformers, or unusual trends. Also call it
    proactively when results contain sequential time-series data (e.g. daily
    or weekly revenue) to check if anything looks off.

    Args:
        rows               : The 'rows' list returned by query_sales_data.
        metric_column      : The column name to analyse (must be numeric).
        threshold_pct_drop : Flag a row if the value is this % below the mean.
                             Default: 20.0 (i.e. 20% below average).
        threshold_pct_spike: Flag a row if the value is this % above the mean.
                             Default: 50.0 (i.e. 50% above average).

    Returns:
        A dict with keys:
          - status         : "success" or "error"
          - anomalies_found: True / False
          - flagged_rows   : list of rows that breached a threshold
          - summary        : Human-readable summary of findings
          - mean_value     : The mean of the metric column across all rows
    """
    try:
        if not rows:
            return {
                "status": "success",
                "anomalies_found": False,
                "flagged_rows": [],
                "summary": "No data to analyse.",
                "mean_value": None,
            }

        # Extract numeric values from the metric column
        values = []
        for row in rows:
            val = row.get(metric_column)
            if val is not None:
                try:
                    values.append(float(val))
                except (TypeError, ValueError):
                    pass

        if not values:
            return {
                "status": "error",
                "anomalies_found": False,
                "flagged_rows": [],
                "summary": f"Column '{metric_column}' not found or contains "
                           f"no numeric values.",
                "mean_value": None,
            }

        mean_val = sum(values) / len(values)
        drop_threshold  = mean_val * (1 - threshold_pct_drop  / 100)
        spike_threshold = mean_val * (1 + threshold_pct_spike / 100)

        flagged = []
        for row in rows:
            val = row.get(metric_column)
            if val is None:
                continue
            try:
                fval = float(val)
            except (TypeError, ValueError):
                continue

            if fval < drop_threshold:
                flagged.append({
                    **row,
                    "_flag": f"⚠️ Low — {((mean_val - fval) / mean_val * 100):.1f}% below average",
                })
            elif fval > spike_threshold:
                flagged.append({
                    **row,
                    "_flag": f"🔺 High — {((fval - mean_val) / mean_val * 100):.1f}% above average",
                })

        if flagged:
            summary = (
                f"Found {len(flagged)} anomalies in '{metric_column}' "
                f"(mean: {mean_val:,.2f}). "
                f"Drops flagged at >{threshold_pct_drop}% below mean, "
                f"spikes at >{threshold_pct_spike}% above mean."
            )
        else:
            summary = (
                f"No anomalies detected in '{metric_column}'. "
                f"All values are within normal range of the mean ({mean_val:,.2f})."
            )

        return {
            "status": "success",
            "anomalies_found": len(flagged) > 0,
            "flagged_rows": flagged,
            "summary": summary,
            "mean_value": round(mean_val, 2),
        }

    except Exception as e:
        return {
            "status": "error",
            "anomalies_found": False,
            "flagged_rows": [],
            "summary": f"Anomaly check failed: {e}",
            "mean_value": None,
        }
