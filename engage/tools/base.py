from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

class BaseIntegration(ABC):
    """Base class for all external service integrations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the integration is working."""
        pass