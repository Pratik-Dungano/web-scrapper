"""
errors.py
Defines custom error classes for input, network, and data extraction errors.
"""

class InvalidURLError(Exception):
    """Raised when a URL is invalid."""
    pass

class URLUnreachableError(Exception):
    """Raised when a URL is not reachable."""
    pass

class NetworkError(Exception):
    """Raised when a network error occurs during fetching."""
    pass

class DataExtractionError(Exception):
    """Raised when required data cannot be extracted from a page."""
    pass
