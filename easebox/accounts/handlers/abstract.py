from abc import abstractclassmethod, abstractmethod
from abc import ABC
from typing import Dict, Optional, Any

class Handler(ABC):

    def __init__(self, type) -> Dict[str, Any]:

        self.HANDLER = self.get(type)
    
    @abstractmethod
    def run(self, *args, **kwargs):
        pass