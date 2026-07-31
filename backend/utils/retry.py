"""
Generic retry utility.
"""

import time
from functools import wraps

from backend.core.logger import logger


def retry(
    retries: int = 3,
    delay: int = 1,
    backoff: int = 2,
):
    """
    Retry decorator with exponential backoff.
    """

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            current_delay = delay

            for attempt in range(1, retries + 1):

                try:
                    return func(*args, **kwargs)

                except Exception as exc:

                    logger.warning(
                        "Retry %s/%s failed: %s",
                        attempt,
                        retries,
                        exc,
                    )

                    if attempt == retries:
                        raise

                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper

    return decorator