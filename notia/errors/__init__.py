from typing import List, Optional


class Error(Exception):
    """Base Error"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message
