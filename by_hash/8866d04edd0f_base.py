from abc import ABC, abstractmethod
from typing import Any, Dict, List
from ..loom.models import LoomWeave

class BaseScanner(ABC):
    """
    The abstract base class for all CodeCity-Bench scanners.
    Scanners are responsible for analyzing a target (files, directories, etc.)
    and producing a 'LoomWeave' representation.
    """

    def __init__(self, target_path: str):
        self.target_path = target_path

    @abstractmethod
    def scan(self) -> LoomWeave:
        """
        Perform the scan and return a LoomWeave object.
        """
        pass

    @abstractmethod
    def get_summary(self) -> Dict[str, Any]:
        """
        Return a summary of the scanning results.
        """
        pass
