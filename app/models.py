from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Book:
    id: int
    title: str
    author: str
    published_year: int
    isbn: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "published_year": self.published_year,
            "isbn": self.isbn,
            "created_at": self.created_at.isoformat(),
        }

@dataclass
class BookV2(Book):
    publisher: Optional[str] = None
    genre: Optional[str] = None
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "publisher": self.publisher,
            "genre": self.genre
        })
        return base_dict

@dataclass
class User:
    id: int
    username: str
    email: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class Review:
    id: int
    book_id: int
    user_id: int
    rating: int
    text: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    def to_dict(self):
        return {
            "id": self.id,
            "book_id": self.book_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
        }

# База данных в памяти
books_db: Dict[int, Book] = {
    1: BookV2(id=1, title="Война и мир", author="Лев Толстой", 
              published_year=1869, genre="Роман-эпопея", 
              publisher="Русский вестник", isbn="978-5-699-13751-1"),
    2: BookV2(id=2, title="Преступление и наказание", 
              author="Фёдор Достоевский", published_year=1866,
              genre="Психологический роман", publisher="Русский вестник",
              isbn="978-5-17-048254-3"),
    3: BookV2(id=3, title="Евгений Онегин", author="Александр Пушкин",
              published_year=1833, genre="Роман в стихах",
              isbn="978-5-389-06215-8"),
    4: BookV2(id=4, title="Отцы и дети", author="Иван Тургенев",
              published_year=1862, genre="Социально-психологический роман",
              publisher="Русский вестник", isbn="978-5-04-106758-3"),
    5: BookV2(id=5, title="Мёртвые души", author="Николай Гоголь",
              published_year=1842, genre="Поэма",
              isbn="978-5-17-112988-2"),
    6: BookV2(id=6, title="Анна Каренина", author="Лев Толстой",
              published_year=1877, genre="Роман",
              publisher="Русский вестник", isbn="978-5-04-103640-4"),
}

users_db: Dict[int, User] = {
    1: User(id=1, username="читатель", email="reader@example.com"),
    2: User(id=2, username="литератор", email="literator@example.com"),
    3: User(id=3, username="критик", email="critic@example.com"),
    4: User(id=4, username="студент", email="student@example.com"),
}

reviews_db: Dict[int, Review] = {
    1: Review(id=1, book_id=1, user_id=1, rating=5,
              text="Величайшее произведение русской литературы!"),
    2: Review(id=2, book_id=1, user_id=2, rating=4,
              text="Глубокое философское произведение."),
    3: Review(id=3, book_id=2, user_id=3, rating=5,
              text="Гениальное исследование человеческой психологии."),
}

idempotency_store: Dict[str, dict] = {}
