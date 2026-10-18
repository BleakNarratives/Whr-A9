"""Service entrypoints for EquiLex backend."""

from .legal_processor import LegalDocumentProcessor
from .tos_handler import TOSHandler

__all__ = ["LegalDocumentProcessor", "TOSHandler"]
