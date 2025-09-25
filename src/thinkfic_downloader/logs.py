import logging
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init

# Inicializar colorama solo para consola
init(autoreset=True)


class ColorFormatter(logging.Formatter):

    COLORS = {
        logging.DEBUG: Fore.BLUE,
        logging.INFO: Fore.CYAN,
        logging.WARNING: Fore.YELLOW,
        logging.ERROR: Fore.RED,
        logging.CRITICAL: Fore.MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelno, "")
        reset = Style.RESET_ALL
        msg = super().format(record)
        return f"{color}{msg}{reset}"


def setup_logger(name: str, kind: str) -> logging.Logger:

    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"{kind}_{timestamp}.log"

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    base_fmt = "%(asctime)s [%(levelname)s] %(message)s"

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(logging.Formatter(base_fmt))

    ch = logging.StreamHandler()
    ch.setFormatter(ColorFormatter(base_fmt))

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
