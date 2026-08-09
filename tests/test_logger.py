import logging
from unittest.mock import patch

from backend.core.logger import setup_logger


def test_setup_logger_returns_existing_logger():
    logger = setup_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.name == "ai_code_review_bot"


def test_setup_logger_configures_logger_when_no_handlers():
    logger = logging.getLogger("ai_code_review_bot")

    original_handlers = logger.handlers[:]
    original_level = logger.level
    original_propagate = logger.propagate

    try:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # Prevent handlers inherited from the root logger
        # from making hasHandlers() return True.
        logger.propagate = False

        logger.setLevel(logging.NOTSET)

        with patch("backend.core.logger.sys.stdout") as mock_stdout:
            configured_logger = setup_logger()

        assert configured_logger is logger
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1

        handler = logger.handlers[0]

        assert isinstance(
            handler,
            logging.StreamHandler,
        )

        assert handler.formatter is not None

        assert handler.formatter._fmt == (
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s | %(message)s"
        )

        assert handler.stream is mock_stdout

    finally:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        for handler in original_handlers:
            logger.addHandler(handler)

        logger.setLevel(original_level)
        logger.propagate = original_propagate