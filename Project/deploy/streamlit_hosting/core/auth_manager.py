"""Wrapper to expose centralized AuthManager from core.auth_manager for deploy copies.

This file intentionally delegates to the central implementation in `core.auth_manager` so
deploy copies don't drift and so authentication logic (bcrypt, migration) remains single-source.
"""

from core.auth_manager import get_auth_manager as _get_core_auth_manager


def get_auth_manager():
    """Return the central AuthManager instance.

    Other deploy modules can import get_auth_manager() from this file to keep imports
    stable while delegating implementation to `core.auth_manager`.
    """
    return _get_core_auth_manager()