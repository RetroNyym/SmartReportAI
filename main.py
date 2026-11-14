import argparse
import logging
import sys

from ai.insights import generate_insights
from ai.summary import generate_summary
from config.loader import load_connections, load_reports
from config.settings import settings
from database.base import read_query
from mail.outlook import send_report
from reports.excel_report import build_excel
from reports.models import ReportResult
from reports.pdf_report import build_pdf

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("SmartReportAI")

FORMATS = ("excel", "pdf")


def run(formats: list[str], send_mail: bool) -> None:
    connections = load_connections()

    results: list[ReportResult] = []
    for report in load_reports():
        log.info("Veri çekiliyor: %s", report["name"])
        df = read_query(connections[report["connection"]], report["query"])
        insights = generate_insights(df) if report.get("insights") else []
        results.append(
            ReportResult(name=report["name"], df=df, chart=report.get("chart"), insights=insights)
        )

    log.info("AI özeti üretiliyor...")
    summary = generate_summary(results)

    files = []
    if "excel" in formats:
        files.append(build_excel(results, summary, settings.report_dir))
    if "pdf" in formats:
        files.append(build_pdf(results, summary, settings.report_dir))
    for path in files:
        log.info("Rapor hazır: %s", path)

    if send_mail:
        log.info("Outlook ile gönderiliyor...")
        send_report(files, summary, [r.name for r in results])
        log.info("Mail gönderildi: %s", settings.mail_to)


def main() -> int:
    parser = argparse.ArgumentParser(description="SmartReportAI - tek tık raporlama")
    parser.add_argument("--send", action="store_true", help="Raporu Outlook ile gönder")
    parser.add_argument(
        "--formats",
        default=",".join(FORMATS),
        help="Çıktı formatları, virgülle ayrılmış: excel,pdf (varsayılan: ikisi)",
    )
    args = parser.parse_args()

    formats = [f.strip().lower() for f in args.formats.split(",") if f.strip()]
    unknown = set(formats) - set(FORMATS)
    if unknown:
        parser.error(f"Bilinmeyen format: {', '.join(sorted(unknown))}")

    try:
        run(formats, send_mail=args.send)
    except Exception:
        log.exception("Rapor oluşturulurken hata oluştu")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
