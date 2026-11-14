from urllib.parse import quote_plus


def build_url(cfg: dict) -> str:
    user = quote_plus(cfg["user"])
    password = quote_plus(cfg["password"])
    host = cfg["host"]
    port = cfg.get("port") or 5432
    database = cfg["database"]
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
