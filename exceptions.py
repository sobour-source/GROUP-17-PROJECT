class BookNotFoundError(Exception):
    """Raised when no book matches the search criteria."""
    pass


class InvalidISBNError(Exception):
    """Raised when a provided ISBN fails format validation."""
    pass


class APIRequestError(Exception):
    """Raised when a network request to an external API fails."""
    pass


class EmptySearchError(Exception):
    """Raised when the user submits an empty search query."""
    pass
