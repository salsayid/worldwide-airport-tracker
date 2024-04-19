from sys import stderr
from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from milestone1db import Milestone1DataBase, Venue, Operator, Forecast, OperatorVenueRelation
import credentials as cred


def add_starter_data(session):
    operator1 = Operator(name='Test Jeffery Danger', average_rating=5)
    session.add(operator1)

    operator2 = Operator(name='Test Stephan Hawkson', average_rating=5)
    session.add(operator2)

    
    restaurant = Venue(name=' Test Indoor Restaurant', venue_lat='40.8207', venue_lon='-96.7005', type='Indoor Restaurant', operators=[operator1])
    session.add(restaurant)

    theater = Venue(name='Test Indoor Theater', venue_lat='40.8207', venue_lon='-96.7005', type='Indoor Theater', operators=[operator1, operator2])
    session.add(theater)

    sports_arena = Venue(name='Test Indoor Sports Arena', venue_lat='40.8207', venue_lon='-96.7005', type='Indoor Sports Arena', operators=[operator2])
    session.add(sports_arena)

    forecast1 = Forecast(date=date(2021, 1, 1), forecastData='Sunny', venueID=1)
    session.add(forecast1)
    
    forecast2 = Forecast(date=date(2021, 1, 2), forecastData='Sunny', venueID=1)
    session.add(forecast2)
    
    forecast3 = Forecast(date=date(2021, 1, 3), forecastData='Sunny', venueID=2)
    session.add(forecast3)
    
    forecast4 = Forecast(date=date(2021, 1, 4), forecastData='Sunny', venueID=2)
    session.add(forecast4)
    
    forecast5 = Forecast(date=date(2021, 1, 5), forecastData='Sunny', venueID=3)
    session.add(forecast5)
    
    forecast6 = Forecast(date=date(2021, 1, 6), forecastData='Sunny', venueID=3)
    session.add(forecast6)

    




def main():
    try:
        url = Milestone1DataBase.construct_mysql_url('localhost', cred.PORT, cred.DATABASE_NAME, cred.USERNAME, cred.PASSWORD)
        milestone_1_database = Milestone1DataBase(url)
        milestone_1_database.drop_all_tables()
        milestone_1_database.ensure_tables_exist()
        print('Tables created.')
        session = milestone_1_database.create_session()
        add_starter_data(session)
        session.commit()
        print('Records created.')
    except SQLAlchemyError as exception:
        print('Database setup failed!', file=stderr)
        print(f'Cause: {exception}', file=stderr)
        exit(1)


if __name__ == '__main__':
    main()
