import json
import logging
import sys


def configure_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(message)s'))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


def safe_scan_log(**payload) -> None:
    allowed = {'scan_id', 'status', 'provider', 'model', 'member_count', 'issue_count', 'processing_ms', 'failure_code'}
    clean = {k: v for k, v in payload.items() if k in allowed}
    logging.getLogger('kk_scanner').info(json.dumps(clean, default=str, ensure_ascii=False))
