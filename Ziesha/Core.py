# -*- coding: utf-8 -*-
"""
ZiePy Core module

Core module
"""
# pylint: disable=C0103

import subprocess as _subp
from abc import abstractmethod as _abstractmethod
from .Exceptions import KeyError as _KeyError
from .Exceptions import InvalidKeyError as _InvalidKeyError

def run_cmd(*cmd):
    """Run commands in terminal."""
    with _subp.Popen(' '.join(cmd), stdout=_subp.PIPE, shell=True) as out:
        return out.communicate()[0].strip().decode("utf-8")


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args,
                                                                  **kwargs)
        return cls._instances[cls]


class Key(str):
    """
    Key/Wallet class.
    
    Args:
        key (str): Key or Wallet address.
        startswith (str, list): String or list of strings that the key must start with.
        amount (float): Amount of Ziesha in the Wallet.

    Raises:
        TypeError: If key is not a string.
        ValueError: If key is empty.
        KeyError: If key does not start with startswith.
        InvalidKeyError: If key is invalid.
        TypeError: If amount is not a number.

    Returns:
        Key: Key object.
    """

    def __new__(cls, key, amount=None, startswith=None):
        """Create a new Key/Wallet class."""
        if isinstance(key, cls):
            return key
        if not isinstance(key, str):
            raise TypeError("Address/Key must be a string.")
        if key == "":
            raise ValueError("Address/Key cannot be empty.")
        if startswith is None:
            startswith = ['z', '0x']
        if isinstance(startswith, str):
            startswith = [startswith]
        if not any([key.startswith(sw) for sw in startswith]):
            raise _KeyError(startswith=startswith)
        startswith = startswith[0][-1] if len(startswith) == 1 else ''.join([
            sw[-1] for sw in startswith])
        if 0 in [k in f"0123456789abcdef{startswith}" for k in key]:
            print(f"0123456789abcdef{startswith[-1]}")
            print(key)
            raise _InvalidKeyError('Enter a valid Ziesha public key/address.')
        if amount is not None:
            if not isinstance(amount, (str, int, float)):
                raise TypeError("Amount must be a number.")
        return super().__new__(cls, key.lower())

    def __init__(self, _, amount=None):
        """Initialize Key."""
        if amount is not None:
            amount = float(amount)
        self._amount = amount
        super().__init__()

    @property
    def amount(self):
        """Get amount of Ziesha in the Wallet."""
        if self._amount is None:
            raise AttributeError("Amount is not set.")
        return self._amount

    def info(self):
        """Print string representation of key info."""
        txt = f'Address : {self}\n'
        if self._amount is not None:
            txt += f'Amount  : {self._amount}ℤ'
        if hasattr(self, 'pending'):
            txt += f'Pending  : {self.pending}'
        print(txt)

    @_abstractmethod
    def send(self, to, amount): raise NotImplementedError


class PubKey(Key):
    """PubKey/Wallet class."""

    def __new__(cls, key, amount=None):
        """Create a new PubKey/Wallet class."""
        return super().__new__(cls, key, amount, '0x')


class MPNWallet(Key):
    """ZWallet class."""

    def __new__(cls, key, amount=None):
        """Create a new ZWallet class."""
        return super().__new__(cls, key, amount, 'z')


class Miner:
    def __init__(self, wallet, token):
        self._wallet = wallet
        self._token = token

    def __repr__(self):
        return f"{self._wallet} - {self._token}"

    @property
    def wallet(self):
        return self._wallet

    @property
    def token(self):
        return self._token
