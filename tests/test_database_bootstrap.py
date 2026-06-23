import unittest
from unittest.mock import patch

from app.database import ensure_database_exists


class EnsureDatabaseExistsTests(unittest.TestCase):
    def test_creates_target_database_if_missing(self):
        fake_cursor = []

        class FakeCursor:
            def execute(self, sql, params=None):
                fake_cursor.append(sql)

            def fetchone(self):
                return None

            def close(self):
                pass

        class FakeConnection:
            def __init__(self):
                self.autocommit = False
                self.cursor_obj = FakeCursor()

            def cursor(self):
                return self.cursor_obj

            def close(self):
                pass

        fake_conn = FakeConnection()

        with patch("app.database.psycopg2.connect", return_value=fake_conn) as connect_mock:
            ensure_database_exists("postgresql://postgres:0000@localhost:5432/fitness_tracker")

        connect_mock.assert_called_once()
        self.assertIn('CREATE DATABASE "fitness_tracker"', "\n".join(fake_cursor))


if __name__ == "__main__":
    unittest.main()
