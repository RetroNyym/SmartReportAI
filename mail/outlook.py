import html
from datetime import datetime
from pathlib import Path
from string import Template

from config.i18n import fmt_datetime, t
from config.settings import ROOT_DIR, settings

TEMPLATE_DIR = ROOT_DIR / "templates"


def render_body(summary: str, report_names: list[str]) -> str:
    """Fill the HTML email template. Placeholders: $greeting, $intro, $summary_title, $summary, $closing, $date, $report_names."""
    template = Template((TEMPLATE_DIR / settings.mail_template).read_text(encoding="utf-8"))
    names = html.escape(", ".join(report_names))
    return template.safe_substitute(
        greeting=t("mail_greeting"),
        intro=t("mail_intro", date=fmt_datetime(datetime.now()), names=names),
        summary_title=t("ai_summary"),
        summary=html.escape(summary).replace("\n", "<br>"),
        closing=t("mail_closing"),
        date=fmt_datetime(datetime.now()),
        report_names=names,
    )


def send_report(files: list[Path], summary: str, report_names: list[str]) -> None:
    """Send the report files through the locally installed Outlook (Windows only)."""
    import win32com.client  # pywin32, imported lazily so the rest works on any OS

    if not settings.mail_to:
        raise ValueError(t("err_mail_to"))

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
