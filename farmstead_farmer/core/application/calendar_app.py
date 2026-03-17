from core.domain.calendar_repositories import CalendarRepository


class CalendarUseCase:
    def __init__(self, repo: CalendarRepository):
        self.repo = repo

    def get_sorts(self, category: str) -> list:
        return self.repo.get_sorts(category.strip().lower())

    def get_sort_details(self, category: str, sort_name: str) -> dict:
        return self.repo.get_sort_details(category.strip().lower(), sort_name.strip())
