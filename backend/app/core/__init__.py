"""Core package initialization."""

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import (
    CarbonSenseException,
    DatabaseException,
    CacheException,
    AIModelException,
    QueryAnalysisException,
    carbonsense_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)

__all__ = [
    "settings",
    "setup_logging",
    "get_logger",
    "CarbonSenseException",
    "DatabaseException",
    "CacheException",
    "AIModelException",
    "QueryAnalysisException",
    "carbonsense_exception_handler",
    "validation_exception_handler",
    "generic_exception_handler",
]
