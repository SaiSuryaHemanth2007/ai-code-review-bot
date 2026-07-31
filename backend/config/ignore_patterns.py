"""
Files and directories to ignore during AI review.
"""

IGNORED_DIRECTORIES = {
    "node_modules",
    "dist",
    "build",
    "vendor",
    "__pycache__",
    ".venv",
    "venv",
    "coverage",
}

IGNORED_FILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Pipfile.lock",
}

IGNORED_SUFFIXES = {
    ".min.js",
    ".min.css",
}