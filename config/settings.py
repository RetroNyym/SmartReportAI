import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    report_dir: Path = ROOT_DIR / os.getenv("REPORT_DIR", "output")

    mail_to: str = os.getenv("MAIL_TO", "")
    mail_cc: str = os.getenv("MAIL_CC", "")
    mail_subject_prefix: str = os.getenv("MAIL_SUBJECT_PREFIX", "[SmartReportAI]")
    mail_template: str = os.getenv("MAIL_TEMPLATE", "email.html")


settings = Settings()
