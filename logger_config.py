import logging


def setup_logger(name: str, level: int = logging.INFO):
    """Create and configure a ``logging.Logger`` instance.

    Parameters
    ----------
    name:
        Name of the logger to configure.
    level:
        Logging level to apply to both the logger and its handler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    # Avoid adding multiple handlers if ``setup_logger`` is called repeatedly
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger
