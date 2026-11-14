from urllib.parse import quote_plus


def build_url(cfg: dict) -> str:
    driver = quote_plus(cfg.get("driver") or "ODBC Driver 17 for SQL Server")
    server = cfg["server"]
    database = cfg["database"]
    trusted = str(cfg.get("trusted", "true")).lower() == "true"

    if trusted:
        return f"mssql+pyodbc://@{server}/{database}?driver={driver}&Trusted_Connection=yes"

    user = quote_plus(cfg["user"])
    password = quote_plus(cfg["password"])
    return f"mssql+pyodbc://{user}:{password}@{server}/{database}?driver={driver}"
