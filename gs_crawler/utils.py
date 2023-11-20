import os
import logging
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
LOGS_PATH = BASE_DIR / 'gs_crawler' / 'gs_crawler_logs'
URLS_PATH = BASE_DIR / 'urls'


def check_for_dirs():
    if not os.path.exists(LOGS_PATH):
        os.mkdir(LOGS_PATH)
    if not os.path.exists(URLS_PATH):
        os.mkdir(URLS_PATH)


def logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    file_handler = logging.FileHandler(
        LOGS_PATH / 'crawler.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


if __name__ == "__main__":
    check_for_dirs()
