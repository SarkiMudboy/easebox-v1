from abc import abstractclassmethod, abstractmethod
from abc import ABC
from typing import Dict, Optional, Any

class Handler(ABC):
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        pass