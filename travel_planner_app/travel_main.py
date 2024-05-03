import math
import os
import csv
from datetime import datetime, timedelta

import requests
from kivy.app import App
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from sqlalchemy.exc import SQLAlchemyError

from database import FinalDatabase, City, Airport

api_key = None
url = None
operator_database = None
session = None
city_names = []
city_locations = []
city_coords = []
airport_names = []
airport_codes = []
airport_coords = []
city_country = None
city_lat = 0
city_lon = 0
current_location = ''
past_travel_data = ''


def show_popup(self, happened, message1, message2):
    content = BoxLayout(orientation='vertical')
    database_info = Label(text=message1, font_size=50, size_hint=(1, 0.8), text_size=(400, None), halign='center',
                          valign='middle')
    new_info = Label(text=message2, font_size=50, size_hint=(1, 0.8), text_size=(400, None), halign='center',
                     valign='middle')
    select_database = Button(text='Choose Database Info', size_hint=(1, 0.2))
    select_new = Button(text='Choose New Info', size_hint=(1, 0.2), on_press=lambda x: self.save_new_info())
    close_button = Button(text='Close', size_hint=(1, 0.2))
    content.add_widget(database_info)
    content.add_widget(new_info)
    content.add_widget(select_database)
    content.add_widget(select_new)
    content.add_widget(close_button)
    popup = Popup(title=happened, content=content, size_hint=(1, 1), size=(400, 200))
    close_button.bind(on_release=popup.dismiss)
    popup.open()


class StartUpScreen(Screen):
    def submit_credentials(self):
        try:
            global url, operator_database, session, api_key, cities
            url = FinalDatabase.construct_mysql_url(self.ids.authority.text, int(self.ids.port_number.text),
                                                    self.ids.database_name.text, self.ids.database_username.text,
                                                    self.ids.database_password.text)
            operator_database = FinalDatabase(url)
            session = operator_database.create_session()
            api_key = self.ids.openweather_key.text

            city_query = session.query(City).all()
            for city in city_query:
                city_names.append(city.name)
                city_locations.append(city.encompassing_entity)
                city_coords.append(city.location)

            airport_query = session.query(Airport).all()
            for airport in airport_query:
                airport_names.append(airport.name)
                airport_codes.append(airport.icao_code)
                airport_coords.append(airport.location)
            print("connection")
        except SQLAlchemyError:
            print("no connection")


class LoadingScreen(Screen):
    pass


class MainMenuScreen(Screen):
    pass


class ValidateLocationsScreen(Screen):
    def save_new_info(self):
        global city_country, city_lon, city_lat
        city_query = session.query(City).filter(City.name == self.ids.ac_name.text).one()
        city_query.encompassing_entity = city_country
        city_query.location = f"{city_lat},{city_lon}"
        session.add(city_query)
        session.commit()

    def update_city_text(self):
        self.ids.icao_code.text = ""
        index = city_names.index(self.ids.city_spinner.text)
        self.ids.country.text = city_locations[index]
        self.ids.ac_name.text = city_names[index]
        coords = city_coords[index]
        coords_split = coords.split(",")
        self.ids.lat.text = coords_split[0]
        self.ids.lon.text = coords_split[1]

    def update_airport_text(self):
        self.ids.country.text = ""
        index = airport_names.index(self.ids.airport_spinner.text)
        self.ids.icao_code.text = airport_codes[index]
        self.ids.ac_name.text = airport_names[index]
        coords = airport_coords[index]
        coords_split = coords.split(",")
        self.ids.lat.text = coords_split[0]
        self.ids.lon.text = coords_split[1]

    def validate(self):
        global session
        if self.ids.icao_code.text == "":
            global api_key, city_country, city_lon, city_lat
            url = f"http://api.openweathermap.org/geo/1.0/direct?q={self.ids.ac_name.text}&appid={api_key}"
            response = requests.get(url)
            openweather_data = response.json()
            if response.status_code == 200:
                city_lat = openweather_data[0]['lat']
                city_lon = openweather_data[0]['lon']
                city_country = openweather_data[0]['country']

                if str(city_lat) == self.ids.lat.text and str(city_lon) == self.ids.lon.text and str(
                        city_country) == self.ids.country.text:
                    show_popup(self, "Information Validated", "The city has been validated", "")
                else:
                    data_info = f"Database Info:\nName: {self.ids.ac_name.text}, Country: {self.ids.country.text}\nLat: {self.ids.lat.text}, Lon: {self.ids.lon.text}"
                    new_info = f"New Info:\nName: {self.ids.ac_name.text}, Country: {city_country}\nLat: {city_lat}, Lon: {city_lon}"
                    show_popup(self, "Choose Correct Information", data_info, new_info)
            else:
                show_popup(self, "Failure", "City cannot be validated", "Please select a different city")
        elif self.ids.country.text == "":
            location = list(filter(lambda code: code['ICAO'] == self.ids.icao_code.text, data))
            dictionary = location[0]
            icao = dictionary['ICAO']
            name = dictionary['Name']
            country = dictionary['Country']
            latitude = dictionary['Latitude']
            longitude = dictionary['Longitude']

    def refresh(self):
        self.ids.city_spinner.values = city_names
        self.ids.airport_spinner.values = airport_names
        self.ids.icao_code.text = ""
        self.ids.country.text = ""
        self.ids.ac_name.text = ""
        self.ids.lat.text = ""
        self.ids.lon.text = ""


class UpdateRatingsScreen(Screen):
    pass


def calculate_distance(location1, location2):
    R = 6371
    lat1, lon1 = location1['latitude'], location1['longitude']
    lat2, lon2 = location2['latitude'], location2['longitude']
    d = math.acos(math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) +
                  math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                  math.cos(math.radians(lon2 - lon1))) * R
    return d


class PrepareItineraryScreen(Screen):
    current_location = StringProperty('Lincoln, Nebraska')
    days_into_journey = NumericProperty(0)

    def update_info(self, location, day):        self.current_location = location

        self.days_into_journey = day

    def city_with_most_activities(self):
        pass

    def city_farthest_away(self):
        pass

    def city_in_range(self, cities, current_location):
        cites = []
        for city in cities:
            for location in city:
                if self._calculate_distance(current_location, location) < 15000:
                    return True
                else:
                    return False


def generate_itinerary_2(self, current_location, past_travel_data):
    itinerary = [past_travel_data]
    next_location = self.city_with_most_activities()
    arrival_date = datetime.now() + timedelta(days=1)
    itinerary.append({'from': current_location['name'], 'to': next_location['name'], 'departure_date': datetime.now(),
                      'arrival_date': arrival_date})
    return itinerary


def generate_itinerary_1(self, current_location, past_travel_data):
    itinerary = [past_travel_data]
    next_location = self.city_farthest_away()
    arrival_date = datetime.now() + timedelta(days=1)
    itinerary.append({'from': current_location['name'], 'to': next_location['name'],
                      'departure_date': datetime.now(), 'arrival_date': arrival_date})
    return itinerary


class ReviewItineraryScreen(Screen):
    itinerary_1 = generate_itinerary_1(current_location, past_travel_data)
    itinerary_2 = generate_itinerary_2(current_location, past_travel_data)


class TravelPlannerApp(App):

    def build(self):
        inspector.create_inspector(Window, self)  # For inspection (press control-e to toggle).


if __name__ == '__main__':
    parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    file_path = os.path.join(parent_directory, "travel_planner_app", "airports.csv")
    with open(file_path) as file:
        data = []
        csv = csv.DictReader(file)
        for row in csv:
            data.append(row)
    app = TravelPlannerApp()
    app.run()
