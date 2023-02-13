# -*- coding: utf-8 -*-
"""
ZiePy Exceptions module

~~~~~~~~~~~~~~~~~~~~~
This module contains custom exceptions for ZiePy.
"""
# pylint: disable=C0103


class KeyError(Exception):
    """Exception raised when there is an error with the Key."""

    def __init__(self, message=None, startswith=None):
        """
        Create a KeyError.

        Args:
            message (str): Error message.
        
        Returns:
            KeyError: KeyError object.
        """
        if not startswith is None:
            if isinstance(startswith, str):
                startswith = [startswith]
            if message is None:
                if len(startswith) == 1:
                    startswith = startswith[0]
                message = f"Key must start with '{startswith}'."
        if message is None:
            message = f"An error occured with the Key."
        self.message = message
        super().__init__(self.message)


class InvalidKeyError(KeyError):
    """Exception raised when the Key is invalid."""

    def __init__(self, message=None):
        """
        Create a InvalidKeyError.

        Args:
            message (str): Error message.
        
        Returns:
            KeyError: KeyError object.
        """
        if message is None:
            message = f"Key is invalid."
        self.message = message
        super().__init__(self.message)


class FaucetDurationError(Exception):
    """Exception raised when time between faucet requests is too short."""

    def __init__(self, cool_down_sec, total_seconds):
        """
        Create a FaucetDurationError.

        Args:
            message (str): Error message.
        
        Returns:
            KeyError: KeyError object.
        """
        m, s = divmod(cool_down_sec - total_seconds, 60)
        h, m = divmod(m, 60)
        dur = f"{int(h):02d} hours {int(m):02d} min {int(s):02d} sec"
        self.message = f"You have to wait {dur}."
        super().__init__(self.message)
