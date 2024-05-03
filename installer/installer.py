from datetime import datetime
from sys import stderr

import requests
from sqlalchemy.exc import SQLAlchemyError
from database import FinalDatabase, Airport, City, Forecast, Operator, Venue, Reviews
import os
import json


def add_starter_data(session):
    
    #Package Deal App
    operator1 = Operator(name='Test Jeffery Danger', average_rating=5)
    review1 = Reviews(review='He is a really good operator')
    operator1.reviews = [review1]
    session.add(operator1)
    session.add(review1)

    operator2 = Operator(name='Test Stephan Hawkson', average_rating=5)
    review2 = Reviews(review='He is a really bad operator')
    operator2.reviews = [review2]
    session.add(operator2)
    session.add(review2)

    restaurant = Venue(name=' Test Indoor Restaurant', latitude='40.8207', longitude='-96.7005',
                       type='Indoor Restaurant', operators=[operator1])
    session.add(restaurant)

    theater = Venue(name='Test Indoor Theater', latitude='40.8207', longitude='-96.7005', type='Indoor Theater',
                    operators=[operator1, operator2], average_rating=4.5, reviews='3,4,5,6,7')
    session.add(theater)

    sports_arena = Venue(name='Test Indoor Sports Arena', latitude='40.8207', longitude='-96.7005',
                         type='Indoor Sports Arena', operators=[operator2])
    session.add(sports_arena)

    forecast1 = Forecast(date=datetime(2021, 1, 1), forecastData='overcast clouds', venueID=1)
    session.add(forecast1)

    forecast2 = Forecast(date=datetime(2021, 1, 2), forecastData='light rain', venueID=1)
    session.add(forecast2)

    forecast3 = Forecast(date=datetime(2021, 1, 3), forecastData='overcast clouds', venueID=2)
    session.add(forecast3)

    forecast4 = Forecast(date=datetime(2021, 1, 4), forecastData='light rain', venueID=2)
    session.add(forecast4)

    forecast5 = Forecast(date=datetime(2021, 1, 5), forecastData='overcast clouds', venueID=3)
    session.add(forecast5)

    forecast6 = Forecast(date=datetime(2021, 1, 6), forecastData='light rain', venueID=3)
    session.add(forecast6)
    
    city1 = City(name='London', encompassing_entity='GB', location='51.5073219,-0.1276474')
    city2 = City(name='Omaha', encompassing_entity='US', location='41.2587459,-95.9383758')

    airport1 = Airport(name='London City Airport', icao_code='EGLC', location='51.505299,0.055278')
    airport2 = Airport(name='Eppley Airfield', icao_code='KOMA', location='41.3032,-95.894096')
    airport1.forecasts = [forecast1]
    airport2.forecasts = [forecast3]
    airport1.cities = [city1]
    airport2.cities = [city2]

    session.add(city1)
    session.add(city2)
    session.add(airport1)
    session.add(airport2)
    
    #TODO Add airport data here, idk the format of the data so I can't add it


def main():
    try:
        parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        file_path = os.path.join(parent_directory, "installer", "credentials.json")
        with open(file_path, 'r') as file:
            credential_information = json.load(file)
        authority = credential_information['AUTHORITY']
        port = credential_information['PORT']
        database_name = credential_information['DATABASE_NAME']
        username = credential_information['USERNAME']
        password = credential_information['PASSWORD']
    except FileNotFoundError:
        print('Could not find credentials.json file!', file=stderr)
        exit(1)
    

    try:
        url = FinalDatabase.construct_mysql_url(authority, port, database_name, username, password)
        final_database = FinalDatabase(url)
        final_database.drop_all_tables()
        final_database.ensure_tables_exist()
        print('Tables created.')
        session = final_database.create_session()
        add_starter_data(session)
        session.commit()
        print('Records created.')
    except SQLAlchemyError as e:
        print('Database setup failed!', file=stderr)
        print(f'Cause: {e}', file=stderr)
        exit(1)


if __name__ == '__main__':
    main()
