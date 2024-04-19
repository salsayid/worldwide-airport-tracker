import datetime
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Persisted = declarative_base()
city_airport_association = Table(
    'city_airport', Persisted.metadata,
    Column('city_id', Integer, ForeignKey('cities.city_id')),
    Column('airport_id', Integer, ForeignKey('airports.airport_id'))
)

class Airport(Persisted):
    __tablename__ = 'airports'
    airport_id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    icao_code = Column(String(4), unique=True)
    location = Column(String(256))
    forecasts = relationship('Forecast', back_populates='airport')
    cities = relationship('City', secondary=city_airport_association, back_populates='airports')

class City(Persisted):
    __tablename__ = 'cities'
    city_id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    encompassing_entity = Column(String(256))
    location = Column(String(256))
    airports = relationship('Airport', secondary=city_airport_association, back_populates='cities')

class Forecast(Persisted):
    __tablename__ = 'forecasts'
    forecast_id = Column(Integer, primary_key=True)
    airport_id = Column(Integer, ForeignKey('airports.airport_id'))
    forecast_data = Column(String(1024))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    airport = relationship('Airport', back_populates='forecasts')

class AirportDatabase:
    def __init__(self, url):
        self.engine = create_engine(url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.create_session()

    @staticmethod
    def construct_mysql_url(host, port, database, username, password):
        return f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}'

    def create_session(self):
        return self.Session()

    def ensure_tables_exist(self):
        Persisted.metadata.create_all(self.engine)

    def create_airport(self, name, icao_code, location):
        airport = Airport(name=name, icao_code=icao_code, location=location)
        self.session.add(airport)
        self.session.commit()
        return airport

    def create_city(self, name, encompassing_entity, location):
        city = City(name=name, encompassing_entity=encompassing_entity, location=location)
        self.session.add(city)
        self.session.commit()
        return city
