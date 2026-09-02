import re
import requests
from book import Book
from exceptions import BookNotFoundError, InvalidISBNError, APIRequestError, EmptySearchError


class OpenLibraryClient:
    """Handles all communication with the Open Library API."""

    SEARCH_URL = "https://openlibrary.org/search.json"
    ISBN_URL = "https://openlibrary.org/isbn/{}.json"
    SUBJECT_URL = "https://openlibrary.org/subjects/{}.json"
    TIMEOUT = 8  # seconds

    def search(self, query, search_type="title", limit=10):
        """
        Search by 'title', 'author', or 'isbn'. Returns a list of Book objects.
        Raises EmptySearchError, InvalidISBNError, BookNotFoundError, or APIRequestError.
        """
        query = (query or "").strip()
        if not query:
            raise EmptySearchError("Search query cannot be empty.")

        if search_type == "isbn":
            return [self.get_by_isbn(query)]

        params = {search_type: query, "limit": limit}

        try:
            response = requests.get(self.SEARCH_URL, params=params, timeout=self.TIMEOUT)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise APIRequestError(f"Could not reach Open Library: {e}")

        docs = response.json().get("docs", [])
        if not docs:
            raise BookNotFoundError(f"No books found for {search_type} '{query}'.")

        return [Book.from_openlibrary_doc(doc) for doc in docs]

    def get_by_isbn(self, isbn):
        """Fetch a single book by ISBN, validating the format first."""
        if not Book.validate_isbn(isbn):
            raise InvalidISBNError(f"'{isbn}' is not a valid ISBN-10 or ISBN-13.")

        cleaned = re.sub(r"[\s-]", "", isbn)

        try:
            response = requests.get(self.ISBN_URL.format(cleaned), timeout=self.TIMEOUT)
        except requests.exceptions.RequestException as e:
            raise APIRequestError(f"Could not reach Open Library: {e}")

        if response.status_code == 404:
            raise BookNotFoundError(f"No book found for ISBN '{isbn}'.")
        response.raise_for_status()

        doc = response.json()
        year = Book.extract_year(doc.get("publish_date", ""))
        cover_ids = doc.get("covers", [])
        cover_url = f"https://covers.openlibrary.org/b/id/{cover_ids[0]}-L.jpg" if cover_ids else None

        return Book(
            title=doc.get("title", "Unknown Title"),
            authors=["Unknown Author"],  # the /isbn/ endpoint doesn't include author names directly
            first_publish_year=year,
            subjects=doc.get("subjects", [])[:8],
            page_count=doc.get("number_of_pages"),
            cover_url=cover_url,
            isbn=cleaned,
            open_library_key=doc.get("key"),
        )

    def find_similar(self, book, limit=5):
        """Suggest similar books based on the book's first subject, falling back to its author."""
        candidates = []

        if book.subjects:
            subject = book.subjects[0]
            slug = subject.lower().replace(" ", "_").replace(",", "")
            try:
                response = requests.get(self.SUBJECT_URL.format(slug),
                                         params={"limit": limit + 3}, timeout=self.TIMEOUT)
                response.raise_for_status()
                works = response.json().get("works", [])
                candidates.extend(Book.from_subject_work(w, subject) for w in works)
            except requests.exceptions.RequestException:
                pass  # subject lookup is best-effort; fall through to author search

        if len(candidates) < limit and book.authors and book.authors[0] != "Unknown Author":
            try:
                more = self.search(book.authors[0], search_type="author", limit=limit + 3)
                candidates.extend(more)
            except (BookNotFoundError, APIRequestError):
                pass

        seen = {book.title.lower()}
        unique = []
        for candidate in candidates:
            if candidate.title.lower() not in seen:
                unique.append(candidate)
                seen.add(candidate.title.lower())

        return unique[:limit]

