from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Persisted = declarative_base()


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



class PackageDealDb(object):
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
    
    # Yeet
    
    def create_new_venue(self, name, venue_lat, venue_lon, type):
        venue = Venue(name=name, venue_lat=venue_lat, venue_lon=venue_lon, type=type)
        self.session.add(venue)
        self.session.commit()
        return venue

    def create_new_operator(self, name, average_rating):
        operator = Operator(name=name, average_rating=average_rating)
        self.session.add(operator)
        self.session.commit()
        return operator
    
    def edit_operator(self, operatorID, name, average_rating):
        operator = self.session.query(Operator).filter(Operator.operatorID == operatorID).first()
        operator.name = name
        operator.average_rating = average_rating
        self.session.commit()
        return operator
    
    def store_forecast(self, date, forecastData, venueID):
        forecast = Forecast(date=date, forecastData=forecastData, venueID=venueID)
        self.session.add(forecast)
        self.session.commit()
        return forecast

    def find_if_venue_exists(self, venue_name, venue_lat, venue_lon, venue_type):
        venue = self.session.query(Venue).filter_by(name=venue_name, venue_lat=venue_lat, venue_lon=venue_lon, type=venue_type).first()
        return venue is not None