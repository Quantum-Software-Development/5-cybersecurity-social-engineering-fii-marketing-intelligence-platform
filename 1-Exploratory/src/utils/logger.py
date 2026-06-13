"""
src/utils/logger.py
Investor Intelligence Platform - FIIs Brasil
Centralized structured logging for all pipeline stages.
"""

import logging, sys
from pathlib import Path
from datetime import datetime


def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-28s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    try:
        logs_dir = Path(__file__).parent.parent.parent / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        fh = logging.FileHandler(logs_dir / f"fii_{date_str}.log", encoding="utf-8")
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    except Exception:
        pass
    logger.propagate = False
    return logger


def ingestion_logger()  -> logging.Logger: return get_logger("fii.ingestion")
def etl_logger()        -> logging.Logger: return get_logger("fii.etl")
def nlp_logger()        -> logging.Logger: return get_logger("fii.nlp")
def api_logger()        -> logging.Logger: return get_logger("fii.api")
def dashboard_logger()  -> logging.Logger: return get_logger("fii.dashboard")


def log_source_success(logger, source: str, count: int):
    logger.info(f"SOURCE_OK   | {source} | articles={count}")

def log_source_failure(logger, source: str, error: str):
    logger.warning(f"SOURCE_FAIL | {source} | {str(error)[:120]}")

def log_retry(logger, source: str, attempt: int, max_retries: int):
    logger.warning(f"RETRY       | {source} | {attempt}/{max_retries}")

def log_timeout(logger, source: str, timeout: float):
    logger.warning(f"TIMEOUT     | {source} | {timeout}s")

def log_duplicate(logger, url: str):
    logger.debug(f"DUPLICATE   | {url[:80]}")

def log_dataset_frozen(logger, path: str, count: int):
    logger.info(f"FREEZE_OK   | {path} | records={count}")

def log_api_fallback(logger, endpoint: str):
    logger.warning(f"API_FALLBACK| {endpoint} | loading Gold parquet")

def log_spark_start(logger, app: str, version: str):
    logger.info(f"SPARK_START | app={app} | version={version}")

def log_quality_check(logger, layer: str, passed: bool, detail: str):
    fn = logger.info if passed else logger.warning
    status = "PASS" if passed else "WARN"
    fn(f"QC_{status}     | {layer} | {detail}")
