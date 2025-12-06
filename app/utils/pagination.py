from typing import List

class Paginator:
    def __init__(self, items: List, page: int = 1, per_page: int = 10):
        self.items = items
        self.page = page
        self.per_page = min(per_page, 100)  # максимум 100
        self.total = len(items)
    
    def paginate(self) -> List:
        """Возвращает элементы текущей страницы"""
        start = (self.page - 1) * self.per_page
        end = start + self.per_page
        return self.items[start:end]
    
    def get_pagination_metadata(self) -> dict:
        """Возвращает метаинформацию о пагинации"""
        pages = (self.total + self.per_page - 1) // self.per_page
        
        return {
            "page": self.page,
            "per_page": self.per_page,
            "total": self.total,
            "pages": pages,
            "has_next": self.page < pages,
            "has_prev": self.page > 1,
            "next_page": self.page + 1 if self.page < pages else None,
            "prev_page": self.page - 1 if self.page > 1 else None
        }
