from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from config.i18n import t

from . import mysql, postgresql, sqlite, sqlserver

URL_BUILDERS = {
    "sqlserver": sqlserver.build_url,
    "mysql": mysql.build_url,
    "postgresql": postgresql.build_url,
    "sqlite": sqlite.build_url,
}


def get_engine(conn_cfg: dict) -> Engine:
    db_type = conn_cfg["type"]
    if db_type not in URL_BUILDERS:
        raise ValueError(t("err_db_type", db_type=db_type))
    return create_engine(URL_BUILDERS[db_type](conn_cfg), pool_pre_ping=True)


def read_query(conn_cfg: dict, query_file: str) -> pd.DataFrame:
    """Run a .sql file against the given connection and return the result as a DataFrame."""
    sql = Path(query_file).read_text(encoding="utf-8")
    engine = get_engine(conn_cfg)
    try:
        with engine.connect() as conn:
            return pd.read_sql_query(sql, conn)
    finally:
        engine.dispose()
