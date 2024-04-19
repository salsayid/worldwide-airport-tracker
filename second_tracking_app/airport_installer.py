import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from datetime import datetime
from airport import Airport, City, Forecast, AirportDatabase

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
        api_key = "b35d2791970e14588d0fcdb917c4c7ff"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={icao_code}&appid={api_key}"
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


class AirportApp(App):
    def build(self):
        url = AirportDatabase.construct_mysql_url('localhost', 3306, 'salsayid2', 'salsayid2', 'cho1ooWaew9u')
        db = AirportDatabase(url)
        session = db.create_session()
        db.ensure_tables_exist()

        sm = ScreenManagement()
        sm.session = session
        return sm

if __name__ == '__main__':
    AirportApp().run()