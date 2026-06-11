# tools/summarizer.py
# Formats raw BigQuery results into readable business summaries.


def summarize_results(
    rows: list,
    columns: list,
    question: str,
    format: str = "table",
) -> dict:
    """
    Formats raw query results into a readable business summary.

    Use this tool after query_sales_data returns results, to present data
    clearly to the user. Do not show raw JSON rows directly to the user —
    always pass them through this tool first.

    Args:
        rows     : The 'rows' list returned by query_sales_data.
        columns  : The 'columns' list returned by query_sales_data.
        question : The original user question (used to tailor the summary).
        format   : Output format — "table", "bullets", or "headline".
                   - table    : Markdown table (best for multi-column results)
                   - bullets  : Bullet list (best for rankings or top-N results)
                   - headline : Single sentence (best for single KPI answers)

    Returns:
        A dict with keys:
          - status          : "success" or "error"
          - formatted_output: A markdown-formatted string ready to show the user
          - row_count       : Number of rows summarised
    """
    try:
        if not rows:
            return {
                "status": "success",
                "formatted_output": "No data found for that query. "
                                    "Try adjusting the date range or filters.",
                "row_count": 0,
            }

        output_lines = []

        if format == "headline" or len(rows) == 1:
            row = rows[0]
            pairs = [f"**{k}**: {v}" for k, v in row.items()]
            output_lines.append(" | ".join(pairs))

        elif format == "bullets":
            for i, row in enumerate(rows, 1):
                values = list(row.values())
                label = str(values[0])
                rest = " | ".join(str(v) for v in values[1:])
                output_lines.append(f"{i}. **{label}** — {rest}")

        else:  # table (default)
            # Header row
            header = " | ".join(f"**{c}**" for c in columns)
            separator = " | ".join("---" for _ in columns)
            output_lines.append(header)
            output_lines.append(separator)
            # Data rows
            for row in rows:
                line = " | ".join(str(row.get(c, "")) for c in columns)
                output_lines.append(line)

        output_lines.append(f"\n*{len(rows)} rows returned.*")

        return {
            "status": "success",
            "formatted_output": "\n".join(output_lines),
            "row_count": len(rows),
        }

    except Exception as e:
        return {
            "status": "error",
            "formatted_output": f"Could not format results: {e}",
            "row_count": 0,
        }
