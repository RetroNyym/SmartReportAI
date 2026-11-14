from urllib.parse import quote_plus


def build_url(cfg: dict) -> str:
    user = quote_plus(cfg["user"])
    password = quote_plus(cfg["password"])
    host = cfg["host"]
    port = cfg.get("port") or 3306
    database = cfg["database"]
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
