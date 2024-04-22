from sqlalchemy import create_engine, Column, Integer, String, Date, Table, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

Persisted = declarative_base()

city_airport_association = Table(
    'city_airport', Persisted.metadata,
    Column('city_id', Integer, ForeignKey('cities.city_id')),
    Column('airport_id', Integer, ForeignKey('airports.airport_id'))
)

class Venue(Persisted):
    __tablename__ = 'venue'
    
    venueID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    venue_lat = Column(String(256), nullable=False)
    venue_lon = Column(String(256), nullable=False)
    type = Column(String(256), nullable=False)
    
    operators = relationship('Operator', secondary='operator_venue_relation', back_populates='venues')


class Operator(Persisted):
    __tablename__ = 'operator'

    operatorID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    average_rating = Column(Integer, nullable=False)
    
    venues = relationship('Venue', secondary='operator_venue_relation', back_populates='operators')


class Forecast(Persisted):
    __tablename__ = 'forecast'

    forecastID = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    forecastData = Column(String(256), nullable=False)
    venueID = Column(Integer, ForeignKey('venue.venueID'))
    
    venue = relationship('Venue', backref='forecasts')


class OperatorVenueRelation(Persisted):
    __tablename__ = 'operator_venue_relation'
    operatorID = Column(Integer, ForeignKey('operator.operatorID'), primary_key=True)
    venueID = Column(Integer, ForeignKey('venue.venueID'), primary_key=True)

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



class FinalDatabase(object):
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
