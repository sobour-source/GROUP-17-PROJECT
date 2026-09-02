import json
import os
from book import Book


class ReadingListManager:
    """Tracks the user's saved books and reading status, and saves/loads them as JSON."""

    VALID_STATUSES = ("Want to Read", "Reading", "Finished")

    def __init__(self, filepath="reading_list.json"):
        self.filepath = filepath
        self.books = {}  # keyed by lowercase title, so the same book isn't added twice

    def add_book(self, book, status="Want to Read"):
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Status must be one of {self.VALID_STATUSES}")
        book.status = status
        self.books[book.title.lower()] = book

    def update_status(self, title, status):
        key = title.lower()
        if key not in self.books:
            raise KeyError(f"'{title}' is not in your reading list.")
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Status must be one of {self.VALID_STATUSES}")
        self.books[key].status = status

    def remove_book(self, title):
        self.books.pop(title.lower(), None)

    def get_by_status(self, status):
        return [b for b in self.books.values() if b.status == status]

    def all_books(self):
        return list(self.books.values())

    def save(self):
        data = [book.to_dict() for book in self.books.values()]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if not os.path.exists(self.filepath):
            return  # nothing saved yet — start with an empty list
        with open(self.filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                return  # corrupted or empty file — start fresh rather than crash
        self.books = {}
        for entry in data:
            book = Book.from_dict(entry)
            self.books[book.title.lower()] = book
