import pandas as pd

from config.i18n import fmt_number, t

CHANGE_THRESHOLD_PCT = 20.0
COMPARE_PERIODS = 3


def generate_insights(df: pd.DataFrame) -> list[str]:
    """
    Rule-based trend analysis for time-ordered data.
    First column = period label, second column = numeric value.
    The last period is compared with the average of the previous COMPARE_PERIODS periods.
    """
    if df.empty or len(df.columns) < 2:
        return []

    labels = df.iloc[:, 0].astype(str).tolist()
    values = pd.to_numeric(df.iloc[:, 1], errors="coerce").fillna(0).tolist()
    if len(values) < COMPARE_PERIODS + 1:
        return []

    lines = []
    last_label, last_value = labels[-1], values[-1]
    baseline = sum(values[-COMPARE_PERIODS - 1 : -1]) / COMPARE_PERIODS

    if baseline != 0:
        change = (last_value - baseline) / abs(baseline) * 100
        if abs(change) >= CHANGE_THRESHOLD_PCT:
            direction = t("insight_drop") if change < 0 else t("insight_rise")
            lines.append(
                t(
                    "insight_change",
                    label=last_label,
                    periods=COMPARE_PERIODS,
                    pct=f"{abs(change):.0f}",
                    direction=direction,
                )
            )
            if change <= -CHANGE_THRESHOLD_PCT:
                lines.append(t("insight_review"))

    peak_index = max(range(len(values)), key=lambda i: values[i])
    lines.append(t("insight_peak", label=labels[peak_index], value=fmt_number(values[peak_index])))

    return lines
