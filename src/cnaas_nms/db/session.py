import os
import yaml
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from pymongo import MongoClient
from redis import StrictRedis


def get_dbdata(config='/etc/cnaas-nms/db_config.yml'):
    with open(config, 'r') as db_file:
        return yaml.safe_load(db_file)


def get_sqlalchemy_conn_str(**kwargs) -> str:
    db_data = get_dbdata(**kwargs)
    if 'CNAAS_DB_HOSTNAME' in os.environ:
        db_data['hostname'] = os.environ['CNAAS_DB_HOSTNAME']
    if 'CNAAS_DB_PORT' in os.environ:
        db_data['port'] = os.environ['CNAAS_DB_PORT']
    if 'CNAAS_DB_USERNAME' in os.environ:
        db_data['username'] = os.environ['CNAAS_DB_USERNAME']
    if 'CNAAS_DB_PASSWORD' in os.environ:
        db_data['password'] = os.environ['CNAAS_DB_PASSWORD']
    if 'CNAAS_DB_DATABASE' in os.environ:
        db_data['database'] = os.environ['CNAAS_DB_DATABSE']

    conn_str = (
        f"{db_data['type']}://{db_data['username']}:{db_data['password']}@"
        f"{db_data['hostname']}:{db_data['port']}/{db_data['database']}"
    )

    return conn_str


@contextmanager
def sqla_session(**kwargs):
    conn_str = get_sqlalchemy_conn_str(**kwargs)

    engine = create_engine(conn_str, poolclass=NullPool)
    connection = engine.connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

@contextmanager
def sqla_execute(**kwargs):
    conn_str = get_sqlalchemy_conn_str(**kwargs)
    engine = create_engine(conn_str)

    with engine.connect() as connection:
        yield connection

@contextmanager
def mongo_db(**kwargs):
    db_data = get_dbdata(**kwargs)
    client = MongoClient(db_data['mongo_hostname'])
    db = client[db_data['database']]
    try:
        yield db
    finally:
        client.close()

@contextmanager
def redis_session(**kwargs):
    db_data = get_dbdata(**kwargs)
    with StrictRedis(host=db_data['redis_hostname'], port=6379) as conn:
        yield conn
