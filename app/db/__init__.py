"""Database package."""

from .connection import get_connection, init_database

__all__ = ['get_connection', 'init_database']
