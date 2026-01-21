import logging
import sys

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
  logger = logging.getLogger(name)

  # 既にハンドラが設定されている場合は再設定しない
  if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
      fmt="[%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)

  return logger
