from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Persisted = declarative_base()

class TravelPlannerDatabase(object):
    @staticmethod
    def construct_mysql_url(authority, port, database, username, password):
        return f'mysql+mysqlconnector://{username}:{password}@{authority}:{port}/{database}'

    @staticmethod
    def construct_in_memory_url():
        return 'sqlite:///'

    def __init__(self, url):
        self.engine = create_engine(url)
        self.Session = sessionmaker()
        self.Session.configure(bind=self.engine)

    def ensure_tables_exist(self):
        Persisted.metadata.create_all(self.engine)

    def drop_all_tables(self):
        Persisted.metadata.drop_all(self.engine)

    def create_session(self):
        return self.Session()