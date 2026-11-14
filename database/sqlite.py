def build_url(cfg: dict) -> str:
    return f"sqlite:///{cfg['path']}"
