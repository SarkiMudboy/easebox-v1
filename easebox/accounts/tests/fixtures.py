from .account_factory import BusinessFactory
from typing import Dict
import factory

class APIData:

    @staticmethod
    def get_business() -> Dict[str, str]:
        return factory.build(dict, FACTORY_CLASS=BusinessFactory)