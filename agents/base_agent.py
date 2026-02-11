"""
Base agent class
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
from core.llm_client import LLMClient
from utils.logger import get_logger

class BaseAgent(ABC):
    """Base class for all agents in the council"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """Process input and return agent output"""
        pass
    
    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format prompt template with variables"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            self.logger.error(f"Missing template variable: {e}")
            raise
