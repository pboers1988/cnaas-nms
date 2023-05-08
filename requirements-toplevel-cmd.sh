# python3 -m pip freeze | egrep "^(SQLAlchemy|nornir|Flask-JWT-Extended|flask-restplus|APScheduler|psycopg2|mypy|sqlalchemy-stubs|nose|GitPython|alembic|Sphinx|coverage|pluggy|redis|Flask-SocketIO|gevent|Flask-Cors|redis-lru)" > requirements.txt
# sqlalchemy-stubs is required for mypy to handle typing definitions from sqlalchemy?
