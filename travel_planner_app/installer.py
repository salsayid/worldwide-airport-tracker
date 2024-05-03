from datetime import datetime
from sys import stderr

import requests
from sqlalchemy.exc import SQLAlchemyError
from database import FinalDatabase, Airport, City, Forecast, Operator, Venue
from kivy.uix.screenmanager import ScreenManager, Screen
import credentials as cred


class ScreenManagement(ScreenManager):
    pass


class MainMenuScreen(Screen):
    pass


class NewAirportScreen(Screen):
    def create_airport(self, name, code, location):
        try:
            if self.manager.session is None:
                raise Exception("Failed to create database session.")

            new_airport = Airport(name=name, icao_code=code, location=location)
            self.manager.session.add(new_airport)
            self.manager.session.commit()
            print("Airport added successfully!")
        except Exception as e:
            print(f"Error adding airport: {e}")
            if self.manager.session:
                self.manager.session.rollback()


class NewCityScreen(Screen):
    def create_city(self, name, entity, location):
        try:
            new_city = City(name=name, encompassing_entity=entity, location=location)
            self.manager.session.add(new_city)
            self.manager.session.commit()
            print("City added successfully!")
        except Exception as e:
            self.manager.session.rollback()
            print(f"Error adding city: {e}")


class CheckForecastScreen(Screen):
    def get_forecast(self, icao_code, date_str):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={icao_code}&appid={cred.API_KEY}"
        try:
            response = requests.get(url)
            data = response.json()
            if response.status_code == 200:
                forecast = data["weather"][0]["description"]
                print(f"Forecast for {icao_code} on {date_str}: {forecast}")
            else:
                print(f"Failed to fetch forecast. Status code: {response.status_code}")
        except Exception as e:
            print("An error occurred:", e)


def add_starter_data(session):
    operator1 = Operator(name='Test Jeffery Danger', average_rating=5)
    session.add(operator1)

    operator2 = Operator(name='Test Stephan Hawkson', average_rating=5)
    session.add(operator2)

    restaurant = Venue(name=' Test Indoor Restaurant', latitude='40.8207', longitude='-96.7005',
                       type='Indoor Restaurant', operators=[operator1])
    session.add(restaurant)

    theater = Venue(name='Test Indoor Theater', latitude='40.8207', longitude='-96.7005', type='Indoor Theater',
                    operators=[operator1, operator2])
    session.add(theater)

    sports_arena = Venue(name='Test Indoor Sports Arena', latitude='40.8207', longitude='-96.7005',
                         type='Indoor Sports Arena', operators=[operator2])
    session.add(sports_arena)

    forecast1 = Forecast(date=datetime(2021, 1, 1), forecastData='Sunny', venueID=1)
    session.add(forecast1)

    forecast2 = Forecast(date=datetime(2021, 1, 2), forecastData='Rainy', venueID=1)
    session.add(forecast2)

    forecast3 = Forecast(date=datetime(2021, 1, 3), forecastData='Sunny', venueID=2)
    session.add(forecast3)

    forecast4 = Forecast(date=datetime(2021, 1, 4), forecastData='Sunny', venueID=2)
    session.add(forecast4)

    forecast5 = Forecast(date=datetime(2021, 1, 5), forecastData='Cloudy', venueID=3)
    session.add(forecast5)

    forecast6 = Forecast(date=datetime(2021, 1, 6), forecastData='Cloudy', venueID=3)
    session.add(forecast6)

    city1 = City(name="Lincoln", encompassing_entity="Nebraska", location="41.4925, 99.9018")
    session.add(city1)

    city2 = City(name="Omaha", encompassing_entity="Nebraska", location="41.2565, -95.9345")
    session.add(city2)

def main():
    try:
        url = FinalDatabase.construct_mysql_url('localhost', cred.PORT, cred.DATABASE_NAME, cred.USERNAME, cred.PASSWORD)
        final_database = FinalDatabase(url)
        final_database.drop_all_tables()
        final_database.ensure_tables_exist()
        print('Tables created.')
        session = final_database.create_session()
        add_starter_data(session)
        session.commit()
        print('Starter Data Added')
        sm = ScreenManagement()
        sm.session = session
        print('Records created.')
    except SQLAlchemyError as e:
        print('Database setup failed!', file=stderr)
        print(f'Cause: {e}', file=stderr)
        exit(1)


if __name__ == '__main__':
    main()
