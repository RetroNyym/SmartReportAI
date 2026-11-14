import html
from datetime import datetime
from pathlib import Path
from string import Template

from config.settings import ROOT_DIR, settings

TEMPLATE_DIR = ROOT_DIR / "templates"


def render_body(summary: str, report_names: list[str]) -> str:
    """Fill the HTML email template. Placeholders: $date, $report_names, $summary."""
    template = Template((TEMPLATE_DIR / settings.mail_template).read_text(encoding="utf-8"))
    return template.safe_substitute(
        date=f"{datetime.now():%d.%m.%Y}",
        report_names=html.escape(", ".join(report_names)),
        summary=html.escape(summary).replace("\n", "<br>"),
    )


def send_report(files: list[Path], summary: str, report_names: list[str]) -> None:
    """Send the report files through the locally installed Outlook (Windows only)."""
    import win32com.client  # pywin32, imported lazily so the rest works on any OS

    if not settings.mail_to:
        raise ValueError("MAIL_TO tanımlı değil (.env dosyasını kontrol edin).")

    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0 = olMailItem
    mail.To = settings.mail_to
    if settings.mail_cc:
        mail.CC = settings.mail_cc
    mail.Subject = f"{settings.mail_subject_prefix} {datetime.now():%d.%m.%Y} - {', '.join(report_names)}"
    mail.HTMLBody = render_body(summary, report_names)
    for file in files:
        mail.Attachments.Add(str(file.resolve()))
    mail.Send()
