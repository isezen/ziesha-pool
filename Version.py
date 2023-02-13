# -*- coding: utf-8 -*-
"""
Ziesha Pool.

Version Module
"""
# pylint: disable=C0103
import subprocess as _subp
POOL = "v0.0.1"


def _get(*cmd):
    """Get version string."""
    with _subp.Popen(cmd, stdout=_subp.PIPE) as out:
        return out.communicate()[0].strip().decode("utf-8").replace('!', '')


def bazuka():
    """Bazuka Version."""
    return _get("bazuka", "--version")


def zoro():
    """Zoro Version."""
    return _get("zoro", "--version").split('\n')[1]


def uzi_pool():
    """Uzi-pool Version."""
    return _get("uzi-pool", "--version").split('\n')[1]


def uzi_miner():
    """Uzi-pool Version."""
    return _get("uzi-miner", "--version").split('\n')[1]

