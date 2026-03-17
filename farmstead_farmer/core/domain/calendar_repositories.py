from abc import ABC, abstractmethod
from typing import List, Optional


class CalendarRepository(ABC):

    @abstractmethod
    def get_sorts(self, category: str) -> List[str]: ...

    @abstractmethod
    def get_sort_details(self, category: str, sort_name: str) -> dict: ...
