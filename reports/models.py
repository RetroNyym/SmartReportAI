from dataclasses import dataclass, field

import pandas as pd


@dataclass
class ReportResult:
    name: str
    df: pd.DataFrame
    chart: str | None = None
    insights: list[str] = field(default_factory=list)
