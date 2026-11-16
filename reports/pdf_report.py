import os
import tempfile
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config.i18n import fmt_datetime, fmt_number, t

from .models import ReportResult

MAX_TABLE_ROWS = 40
WINDOWS_FONT_DIR = Path("C:/Windows/Fonts")
PRIMARY = colors.HexColor("#1F4E78")


def _register_fonts() -> tuple[str, str]:
    """Turkish characters need a Unicode font. Use Arial when available."""
    regular = WINDOWS_FONT_DIR / "arial.ttf"
    bold = WINDOWS_FONT_DIR / "arialbd.ttf"
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("SmartFont", str(regular)))
        pdfmetrics.registerFont(TTFont("SmartFont-Bold", str(bold)))
        return "SmartFont", "SmartFont-Bold"
    return "Helvetica", "Helvetica-Bold"


def _format_value(value) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, float):
        return fmt_number(value, decimals=2)
    return str(value)


def _render_chart(result: ReportResult) -> str | None:
    if not result.chart or len(result.df.columns) < 2 or result.df.empty:
        return None

    labels = result.df.iloc[:, 0].astype(str)
    values = pd.to_numeric(result.df.iloc[:, 1], errors="coerce").fillna(0)

    fig, ax = plt.subplots(figsize=(8, 3.8))
    if result.chart == "pie":
        ax.pie(values, labels=labels, autopct="%1.1f%%")
        ax.axis("equal")
    elif result.chart == "line":
        ax.plot(labels, values, marker="o", color="#1F4E78")
        ax.tick_params(axis="x", rotation=45)
    else:
        ax.bar(labels, values, color="#1F4E78")
        ax.tick_params(axis="x", rotation=45)
    ax.set_title(result.name)
    fig.tight_layout()

    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def _table(df: pd.DataFrame, font: str, bold: str) -> list:
    shown = df.head(MAX_TABLE_ROWS)
    data = [[str(c) for c in shown.columns]]
    data += [[_format_value(v) for v in row] for row in shown.itertuples(index=False)]

    table = Table(data, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTNAME", (0, 0), (-1, 0), bold),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F6FA")]),
            ]
        )
    )
    flowables = [table]
    if len(df) > MAX_TABLE_ROWS:
        note = t("truncated_note", max_rows=MAX_TABLE_ROWS, total=len(df))
        flowables.append(Paragraph(escape(note), ParagraphStyle("note", fontName=font, fontSize=8)))
    return flowables


def build_pdf(results: list[ReportResult], summary_text: str, output_dir: Path) -> Path:
    font, bold = _register_fonts()
    base = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=base["Title"], fontName=bold, fontSize=20, textColor=PRIMARY)
    h2_style = ParagraphStyle("h2", parent=base["Heading2"], fontName=bold, textColor=PRIMARY)
    body_style = ParagraphStyle("body", parent=base["BodyText"], fontName=font, fontSize=10, leading=14)

    story = [
        Paragraph(t("app_title"), title_style),
        Paragraph(f"{t('generated_at')}: {fmt_datetime(datetime.now(), with_time=True)}", body_style),
        Spacer(1, 12),
        Paragraph(t("ai_summary"), h2_style),
    ]
    for line in summary_text.split("\n"):
        if line.strip():
            story.append(Paragraph(escape(line), body_style))

    temp_files = []
    for result in results:
        story.append(Spacer(1, 14))
        story.append(Paragraph(escape(result.name), h2_style))
        for insight in result.insights:
            story.append(Paragraph("• " + escape(insight), body_style))

        chart_path = _render_chart(result)
        if chart_path:
            temp_files.append(chart_path)
            story.append(Image(chart_path, width=16 * cm, height=7.6 * cm))
            story.append(Spacer(1, 6))

        story.extend(_table(result.df, font, bold))

    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"SmartReport_{datetime.now():%Y%m%d_%H%M%S}.pdf"
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    try:
        doc.build(story)
    finally:
        for temp in temp_files:
            os.remove(temp)
    return path
