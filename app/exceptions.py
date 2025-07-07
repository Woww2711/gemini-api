# File: app/exceptions.py

class URLAccessError(Exception):
    """
    Custom exception raised when a remote URL is inaccessible
    (e.g., returns 4xx or 5xx status codes).
    """
    def __init__(self, url: str, status_code: int):
        self.url = url
        self.status_code = status_code
        self.detail = f"Failed to access URL '{url}'. The remote server returned status code: {status_code}."
        super().__init__(self.detail)