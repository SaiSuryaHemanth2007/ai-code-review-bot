"""
Application-wide constants.

This file contains values that remain constant throughout
the application's lifecycle.
"""

# ==========================================================
# Application
# ==========================================================

APP_NAME = "AI Code Review Bot"

APP_VERSION = "1.0.0"

APP_DESCRIPTION = (
    "AI-powered GitHub Pull Request Review Bot"
)

DEBUG = True


# ==========================================================
# API
# ==========================================================

API_PREFIX = "/api/v1"

DEFAULT_RESPONSE_MESSAGE = "Request processed successfully."


# ==========================================================
# OpenAI
# ==========================================================

DEFAULT_OPENAI_MODEL = "gpt-4.1-mini"

DEFAULT_TEMPERATURE = 0.2

MAX_TOKENS = 1000


# ==========================================================
# GitHub
# ==========================================================

GITHUB_API_BASE_URL = "https://api.github.com"


# ==========================================================
# Review Engine
# ==========================================================

SUPPORTED_LANGUAGES = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C",
    "C++",
    "Go",
    "Rust",
]