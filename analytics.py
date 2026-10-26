import io
import base64
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def grade_for_percentage(value):
    if value >= 90: return "A+"
    if value >= 80: return "A"
    if value >= 70: return "B"
    if value >= 60: return "C"
    if value >= 50: return "D"
    if value >= 35: return "E"
    return "F"

def student_report(rows, threshold=50):
    """rows: records with student, subject, max_marks, pass_marks, marks_obtained."""
    if not rows:
        return [], [], {"mean": 0, "median": 0, "minimum": 0, "maximum": 0}
    df = pd.DataFrame(rows)
    df["percentage"] = (df["marks_obtained"] / df["max_marks"]) * 100
    df["passed"] = df["marks_obtained"] >= df["pass_marks"]
    reports = []
    for (student_id, roll_no, name, section), group in df.groupby(
        ["student_id", "roll_no", "name", "section"], dropna=False
    ):
        pct = float(group["percentage"].mean())
        reports.append({
            "student_id": int(student_id), "roll_no": roll_no, "name": name,
            "section": section, "total": float(group["marks_obtained"].sum()),
            "max_total": float(group["max_marks"].sum()), "average": float(group["marks_obtained"].mean()),
            "percentage": pct, "grade": grade_for_percentage(pct),
            "status": "Pass" if bool(group["passed"].all()) else "Fail",
            "below_threshold": pct < threshold
        })
    reports.sort(key=lambda item: item["percentage"], reverse=True)
    values = df["marks_obtained"].to_numpy(dtype=float)
    stats = {
        "mean": float(np.mean(values)), "median": float(np.median(values)),
        "minimum": float(np.min(values)), "maximum": float(np.max(values))
    }
    return reports, df.to_dict(orient="records"), stats

def chart_as_base64(labels, values, title, ylabel):
    fig, ax = plt.subplots(figsize=(7, 3.5))
    if labels:
        ax.bar(labels, values)
        ax.tick_params(axis="x", rotation=25)
    else:
        ax.text(0.5, 0.5, "No data yet", ha="center", va="center")
        ax.set_xticks([])
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=130)
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")
