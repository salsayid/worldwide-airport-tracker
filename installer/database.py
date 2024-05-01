from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import datetime

Persisted = declarative_base()


class Venue(Persisted):
    __tablename__ = 'venues'

    venueID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    latitude = Column(String(256), nullable=False)
    longitude = Column(String(256), nullable=False)
    type = Column(String(50), nullable=False)

    operatorID = Column(Integer, ForeignKey('operators.operatorID'))

    operators = relationship('Operator', back_populates='venues', uselist=True)
    forecasts = relationship('Forecast', back_populates='venue')


class Operator(Persisted):
    __tablename__ = 'operators'

    operatorID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    average_rating = Column(Integer)

    venues = relationship('Venue', back_populates='operators')


class OperatorVenueRelationship(Persisted):
    __tablename__ = 'operator_venues'

    operator_venueID = Column(Integer, primary_key=True, autoincrement=True)

    operatorID = Column(Integer, ForeignKey('operators.operatorID'))
    venueID = Column(Integer, ForeignKey('venues.venueID'))

    operator = relationship('Operator', backref='operator_venues')
    venue = relationship('Venue', backref='operator_venues')


class Forecast(Persisted):
    __tablename__ = 'forecast'

    forecastID = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    forecastData = Column(String(256), nullable=False)

    venueID = Column(Integer, ForeignKey('venues.venueID'))
    airportID = Column(Integer, ForeignKey('airports.airportID'))

    venue = relationship('Venue', back_populates='forecasts')
    airport = relationship('Airport', back_populates='forecasts')


class Airport(Persisted):
    __tablename__ = 'airports'
    airportID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    icao_code = Column(String(4), unique=True)
    location = Column(String(256))

    forecasts = relationship('Forecast', back_populates='airport', cascade='all, delete')
    cities = relationship('City', secondary='airport_city_relation', back_populates='airports')


class City(Persisted):
    __tablename__ = 'cities'
    cityID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(256), nullable=False)
    encompassing_entity = Column(String(256))
    location = Column(String(256))

    airports = relationship('Airport', secondary='airport_city_relation', back_populates='cities', cascade='all, delete')


class AirportCityRelation(Persisted):
    __tablename__ = 'airport_city_relation'
    city_airportID = Column(Integer, primary_key=True, autoincrement=True)

    cityID = Column(Integer, ForeignKey('cities.cityID'), primary_key=True)
    airportID = Column(Integer, ForeignKey('airports.airportID'), primary_key=True)


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
        self.session = self.create_session()

    def ensure_tables_exist(self):
        Persisted.metadata.create_all(self.engine)

    def drop_all_tables(self):
        try:
            AirportCityRelation.__table__.drop(self.engine)
            OperatorVenueRelationship.__table__.drop(self.engine)
            Forecast.__table__.drop(self.engine)
            Venue.__table__.drop(self.engine)
            Operator.__table__.drop(self.engine)
            City.__table__.drop(self.engine)
            Airport.__table__.drop(self.engine)

            #Persisted.metadata.drop_all(self.engine)
        except Exception as e:
            pass

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