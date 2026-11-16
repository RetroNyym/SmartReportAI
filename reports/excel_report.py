from datetime import datetime
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from config.i18n import fmt_datetime, t

from .models import ReportResult

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(bold=True, color="FFFFFF")


def _write_table(ws, df: pd.DataFrame, start_row: int = 1) -> tuple[int, int]:
    """Write a DataFrame as a styled table. Returns (last_row, last_col)."""
    for c_idx, col in enumerate(df.columns, start=1):
        cell = ws.cell(row=start_row, column=c_idx, value=str(col))
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center")

    for r_idx, row in enumerate(df.itertuples(index=False), start=start_row + 1):
        for c_idx, value in enumerate(row, start=1):
            ws.cell(row=r_idx, column=c_idx, value=None if pd.isna(value) else value)

    for c_idx, col in enumerate(df.columns, start=1):
        width = max([len(str(col))] + [len(str(v)) for v in df[col].head(200)]) + 2
        ws.column_dimensions[get_column_letter(c_idx)].width = min(width, 45)

    ws.freeze_panes = ws.cell(row=start_row + 1, column=1)
    return start_row + len(df), len(df.columns)


def _add_chart(ws, last_row: int, anchor: str, kind: str, title: str) -> None:
    """Add a native Excel chart: first column = categories, second numeric column = values."""
    cat_ref = Reference(ws, min_col=1, min_row=2, max_row=last_row)
    val_ref = Reference(ws, min_col=2, min_row=1, max_row=last_row)

    if kind == "pie":
        chart = PieChart()
    elif kind == "line":
        chart = LineChart()
    else:
        chart = BarChart()
        chart.type = "col"

    chart.title = title
    chart.add_data(val_ref, titles_from_data=True)
    chart.set_categories(cat_ref)
    chart.width = 18
    chart.height = 9
    ws.add_chart(chart, anchor)


def build_excel(results: list[ReportResult], summary_text: str, output_dir: Path) -> Path:
    wb = Workbook()

    summary_ws = wb.active
    summary_ws.title = t("sheet_summary")
    summary_ws["A1"] = t("app_title")
    summary_ws["A1"].font = Font(bold=True, size=16, color="1F4E78")
    summary_ws["A2"] = f"{t('generated_at')}: {fmt_datetime(datetime.now(), with_time=True)}"
    summary_ws["A4"] = t("ai_summary")
    summary_ws["A4"].font = Font(bold=True, size=12)
    summary_ws["A5"] = summary_text
    summary_ws["A5"].alignment = Alignment(wrap_text=True, vertical="top")
    summary_ws.merge_cells("A5:H20")
    summary_ws.column_dimensions["A"].width = 18

    row = 22
    insight_lines = [(r.name, line) for r in results for line in r.insights]
    if insight_lines:
        summary_ws.cell(row=row, column=1, value=t("insights_title")).font = Font(bold=True, size=12)
        row += 1
        for name, line in insight_lines:
            summary_ws.cell(row=row, column=1, value=f"{name}: {line}")
            row += 1

    for result in results:
        ws = wb.create_sheet(title=result.name[:31])
        last_row, last_col = _write_table(ws, result.df)
        if result.chart and len(result.df.columns) >= 2 and len(result.df) > 0:
            anchor = f"{get_column_letter(last_col + 2)}2"
            _add_chart(ws, last_row, anchor, result.chart, title=result.name)

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"SmartReport_{datetime.now():%Y%m%d_%H%M%S}.xlsx"
    wb.save(path)
    return path
