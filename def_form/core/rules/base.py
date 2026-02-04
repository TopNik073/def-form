from abc import ABC
from abc import abstractmethod

from def_form.exceptions.base import BaseDefFormException
from def_form.core.rules.context import RuleContext


class Rule(ABC):
    @abstractmethod
    def check(self, context: RuleContext) -> list[BaseDefFormException]:
        raise NotImplementedError
