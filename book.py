import re


class Book:
    """Represents a single book and its details."""

    def __init__(self, title, authors=None, first_publish_year=None,
                 subjects=None, page_count=None, cover_url=None,
                 isbn=None, open_library_key=None):
        self.title = self.clean_text(title)
        self.authors = authors or ["Unknown Author"]
        self.first_publish_year = first_publish_year
        self.subjects = subjects or []
        self.page_count = page_count
        self.cover_url = cover_url
        self.isbn = isbn
        self.open_library_key = open_library_key
        self.status = None          # "Want to Read" / "Reading" / "Finished"
        self.reading_guide = None   # filled in later by ReadingGuideGenerator

    # ---------- regex helpers ----------

    @staticmethod
    def clean_text(text):
        """Collapse extra whitespace and strip stray punctuation from title/author text."""
        if not text:
            return "Unknown"
        text = re.sub(r"\s+", " ", text)
        text = text.strip(" .,-")
        return text

    @staticmethod
    def extract_year(date_string):
        """Pull a 4-digit year out of a messy date string like 'c. 1998' or '1998-05-01'."""
        if not date_string:
            return None
        match = re.search(r"(1[0-9]{3}|20[0-9]{2})", str(date_string))
        return int(match.group(1)) if match else None

    @staticmethod
    def validate_isbn(isbn):
        """True if isbn matches ISBN-10 or ISBN-13 format (dashes/spaces ignored)."""
        if not isbn:
            return False
        cleaned = re.sub(r"[\s-]", "", isbn)
        isbn10_pattern = r"^\d{9}[\dX]$"
        isbn13_pattern = r"^97[89]\d{10}$"
        return bool(re.match(isbn10_pattern, cleaned) or re.match(isbn13_pattern, cleaned))

    # ---------- building from API data ----------

    @classmethod
    def from_openlibrary_doc(cls, doc):
        """Build a Book from one 'doc' entry in an Open Library /search.json response."""
        title = doc.get("title", "Unknown Title")
        authors = doc.get("author_name", ["Unknown Author"])
        year = doc.get("first_publish_year") or cls.extract_year(doc.get("publish_date", ""))
        subjects = doc.get("subject", [])[:8]
        page_count = doc.get("number_of_pages_median")
        cover_id = doc.get("cover_i")
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None
        isbn_list = doc.get("isbn", [])
        isbn = isbn_list[0] if isbn_list else None

        return cls(title=title, authors=authors, first_publish_year=year,
                    subjects=subjects, page_count=page_count, cover_url=cover_url,
                    isbn=isbn, open_library_key=doc.get("key"))

    @classmethod
    def from_subject_work(cls, work, subject_name):
        """Build a Book from one 'work' entry in an Open Library /subjects/{name}.json response."""
        title = work.get("title", "Unknown Title")
        authors = [a.get("name", "Unknown Author") for a in work.get("authors", [])] or ["Unknown Author"]
        year = work.get("first_publish_year")
        cover_id = work.get("cover_id")
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else None

        return cls(title=title, authors=authors, first_publish_year=year,
                    subjects=[subject_name], cover_url=cover_url,
                    open_library_key=work.get("key"))

    # ---------- persistence ----------

    def to_dict(self):
        return {
            "title": self.title,
            "authors": self.authors,
            "first_publish_year": self.first_publish_year,
            "subjects": self.subjects,
            "page_count": self.page_count,
            "cover_url": self.cover_url,
            "isbn": self.isbn,
            "open_library_key": self.open_library_key,
            "status": self.status,
            "reading_guide": self.reading_guide,
        }

    @classmethod
    def from_dict(cls, data):
        book = cls(
            title=data.get("title"),
            authors=data.get("authors"),
            first_publish_year=data.get("first_publish_year"),
            subjects=data.get("subjects"),
            page_count=data.get("page_count"),
            cover_url=data.get("cover_url"),
            isbn=data.get("isbn"),
            open_library_key=data.get("open_library_key"),
        )
        book.status = data.get("status")
        book.reading_guide = data.get("reading_guide")
        return book

    def __repr__(self):
        return f"Book('{self.title}' by {', '.join(self.authors)})"
