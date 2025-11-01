"""
Database Connection Pool Service

Provides efficient database connection pooling for concurrent requests.
"""

import sqlite3
import logging
from pathlib import Path
from threading import Lock
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabasePool:
    """
    Thread-safe database connection pool for SQLite.

    Note: SQLite has limited concurrency support. This pool manages
    connections per thread to avoid locking issues.
    """

    def __init__(self, db_path: str, read_only: bool = False):
        self.db_path = Path(db_path)
        self.read_only = read_only
        self._connections = {}
        self._lock = Lock()
        mode = "read-only" if read_only else "read-write"
        logger.info(f"DatabasePool initialized for: {db_path} (mode: {mode})")

    def _get_thread_id(self):
        """Get current thread identifier"""
        import threading
        return threading.get_ident()

    @contextmanager
    def get_connection(self):
        """
        Get a database connection for the current thread.

        Usage:
            with db_pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks")
        """
        thread_id = self._get_thread_id()

        with self._lock:
            if thread_id not in self._connections:
                try:
                    # Open in read-only immutable mode if specified (prevents database locked errors)
                    # Immutable mode tells SQLite the database won't change, allowing concurrent reads
                    if self.read_only:
                        db_uri = f"file:{self.db_path}?mode=ro&immutable=1"
                        conn = sqlite3.connect(db_uri, uri=True, check_same_thread=False)
                    else:
                        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
                    
                    conn.row_factory = sqlite3.Row
                    
                    # Only enable WAL mode for read-write connections
                    if not self.read_only:
                        conn.execute("PRAGMA journal_mode=WAL")
                    
                    # Increase cache size for better performance
                    conn.execute("PRAGMA cache_size=-64000")  # 64MB
                    self._connections[thread_id] = conn
                    logger.debug(f"Created new connection for thread {thread_id}")
                except Exception as e:
                    logger.error(f"Failed to create database connection: {e}")
                    raise

        connection = self._connections.get(thread_id)
        if not connection:
            raise RuntimeError("Failed to get database connection")

        try:
            yield connection
        except Exception as e:
            logger.error(f"Database operation error: {e}")
            raise

    def close_all(self):
        """Close all connections in the pool"""
        with self._lock:
            for thread_id, conn in self._connections.items():
                try:
                    conn.close()
                    logger.debug(f"Closed connection for thread {thread_id}")
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")

            self._connections.clear()
            logger.info("All database connections closed")

    def execute_query(self, query: str, params: tuple = ()):
        """
        Execute a query and return results.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            List of sqlite3.Row objects
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_one(self, query: str, params: tuple = ()):
        """
        Execute a query and return single result.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Single sqlite3.Row object or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def execute_count(self, query: str, params: tuple = ()) -> int:
        """
        Execute a count query and return the count.

        Args:
            query: SQL query string (should return a single count value)
            params: Query parameters

        Returns:
            Count as integer
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result[0] if result else 0

    def __del__(self):
        """Cleanup connections on deletion"""
        try:
            self.close_all()
        except Exception:
            pass


# Helper function to convert Row to dict
def dict_from_row(row: sqlite3.Row) -> dict:
    """Convert sqlite3.Row to dictionary with UUID conversion"""
    if row is None:
        return None

    result = {}
    for key in row.keys():
        value = row[key]

        # Convert binary UUID fields to hex strings
        if isinstance(value, bytes) and len(value) == 16:
            # This is likely a UUID stored as binary BLOB
            # Convert to hex string with dashes (standard UUID format)
            hex_str = value.hex()
            uuid_str = f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"
            result[key] = uuid_str
        else:
            result[key] = value

    return result


def rows_to_dicts(rows) -> list:
    """Convert list of sqlite3.Row objects to list of dicts"""
    return [dict_from_row(row) for row in rows]


if __name__ == "__main__":
    # Test the database pool
    logging.basicConfig(level=logging.DEBUG)

    pool = DatabasePool("data/tasks.db")

    try:
        # Test query
        with pool.get_connection() as conn:
            cursor = conn.cursor()
            tables = cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            print("Tables:", [dict_from_row(t) for t in tables])

    finally:
        pool.close_all()
