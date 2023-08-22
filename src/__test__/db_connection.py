import os

import pytest

from database.db import DB


@pytest.fixture(scope='function', autouse=True)
def db_connection():
    db_to_delete = DB('test_daily_habit.db')
    yield db_to_delete
    os.remove('test_daily_habit.db')
