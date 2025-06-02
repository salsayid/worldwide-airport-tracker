import math
import os
import csv
import time
from datetime import datetime, timedelta
import logging

# just setting up basic logging functionality
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


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
from pygments.lexers import data
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.util import NoneType

from database import FinalDatabase, City, Airport, Operator, Venue, Forecast

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
operator_names = []
operator_reviews_names = ['Default']
operator_scores = []
operator_average = []
operator_new_score = []
venue_names = []
venue_reviews_names = ['Default']
venue_scores = []
venue_average = []
venue_new_score = []
venue_types = []
forecast_dates = []
forecast_data = []
city_country = None
city_lat = 0
city_lon = 0
current_location = StringProperty('Lincoln, Nebraska')
days_into_journey = 0
current_location_coordinate = '40.7128, -74.0060'
past_travel_data = ''
cities_in_range = []
itinerary_1 = 'itinerary_1'
itinerary_2 = 'itinerary_2'
city_num = 0
airport_num = 0
operator_num = 0
venue_num = 0


def show_choose_popup(self, happened, message1, message2):
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


def show_validated_popup(self, happened, message1):
    content = BoxLayout(orientation='vertical')
    database_info = Label(text=message1, font_size=50, size_hint=(1, 0.8), text_size=(400, None), halign='center', valign='middle')
    close_button = Button(text='Close', size_hint=(1, 0.2))
    content.add_widget(database_info)
    content.add_widget(close_button)
    popup = Popup(title=happened, content=content, size_hint=(1, 1), size=(400, 200))
    close_button.bind(on_release=popup.dismiss)
    popup.open()


def show_fail_popup(self, happened, message1):
    content = BoxLayout(orientation='vertical')
    database_info = Label(text=message1, font_size=50, size_hint=(1, 0.8), text_size=(400, None), halign='center', valign='middle')
    close_button = Button(text='Close', size_hint=(1, 0.2))
    content.add_widget(database_info)
    content.add_widget(close_button)
    popup = Popup(title=happened, content=content, size_hint=(1, 1), size=(400, 200))
    close_button.bind(on_release=popup.dismiss)
    popup.open()


class StartUpScreen(Screen):
    def submit_credentials(self):
        try:
            global url, operator_database, session, api_key
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

            operator_query = session.query(Operator).all()
            for operator in operator_query:
                operator_names.append(operator.name)
                operator_average.append(operator.average_rating)
                operator_scores.append(operator.num_reviews)
                if operator.num_reviews:
                    operator_reviews_names.append(operator.name)

            venue_query = session.query(Venue).all()
            for venue in venue_query:
                venue_names.append(venue.name)
                venue_types.append(venue.type)
                venue_average.append(venue.average_rating)
                venue_scores.append(venue.reviews)
                if venue.reviews:
                    venue_reviews_names.append(venue.name)

            forecast_query = session.query(Forecast).all()
            for forecast in forecast_query:
                forecast_dates.append(forecast.date)
                forecast_data.append(forecast.forecastData)

            self.ids.database_password.text = ""
            self.ids.openweather_key.text = ""
            print("connection")
            self.manager.current = 'LoadingScreen'
        except SQLAlchemyError:
            show_fail_popup(self, "No Connection", "No Connection\n\nPlease check the database or openweather fields")


class LoadingScreen(Screen):
    def on_enter(self):
        global city_num, airport_num, operator_num, venue_num
        for i in range(len(city_names)):
            city_num += 1
        for j in range(len(airport_names)):
            airport_num += 1
        for y in range(len(operator_reviews_names)):
            if operator_reviews_names[y] != "Default":
                operator_num += 1
        for z in range(len(venue_reviews_names)):
            if venue_reviews_names[z] != "Default":
                venue_num += 1

        time.sleep(2.5)
        self.manager.current = 'MainMenuScreen'


class MainMenuScreen(Screen):
    def on_pre_enter(self):
        global city_num, airport_num, operator_num, venue_num
        string = f"Needing Validation:\n\nCities: {city_num}\nAirports: {airport_num}\n\nNeeding Updating:\n\nOperators: {operator_num}\nVenues: {venue_num}"
        self.ids.needing_validation.text = string

    def exit_app(self):
        App.get_running_app().stop()

    def advance_calender(self):
        self.days_into_journey = days_into_journey + 1
        self.ids.location_day_id.text = 'Current Location:' + str(current_location) + '\nNumber of Days:' + str(days_into_journey)


class ValidateLocationsScreen(Screen):
    def on_pre_enter(self):
        global city_names, airport_names
        string = "Needing Validation:\n\nCities: "
        for i in range(len(city_names)):
            if i != len(city_names) - 1:
                string += f"{city_names[i]}, "
            else:
                string += f"{city_names[i]}"
        string += "\nAirports: "
        for j in range(len(airport_names)):
            if j != len(airport_names) - 1:
                string += f"{airport_names[j]}, "
            else:
                string += f"{airport_names[j]}"
        self.ids.validate_list.text = string

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

                if str(city_lat) == self.ids.lat.text and str(city_lon) == self.ids.lon.text and str(city_country) == self.ids.country.text:
                    show_validated_popup(self, "Information Validated", "The city has been validated")
                else:
                    data_info = f"Database Info:\nName: {self.ids.ac_name.text}, Country: {self.ids.country.text}\nLat: {self.ids.lat.text}, Lon: {self.ids.lon.text}"
                    new_info = f"New Info:\nName: {self.ids.ac_name.text}, Country: {city_country}\nLat: {city_lat}, Lon: {city_lon}"
                    show_choose_popup(self, "Choose Correct Information", data_info, new_info)
            else:
                show_fail_popup(self, "Failure", "No record\n\nCity cannot be validated\n\nPlease check your selection")
        elif self.ids.country.text == "":
            location = list(filter(lambda code: code['ICAO'] == self.ids.icao_code.text, data))

            if location:
                dictionary = location[0]
                icao = dictionary['ICAO']
                name = dictionary['Name']
                latitude = dictionary['Latitude']
                longitude = dictionary['Longitude']

                if str(icao) == self.ids.icao_code.text and str(name) == self.ids.ac_name.text and str(latitude) == self.ids.lat.text and str(longitude) == self.ids.lon.text:
                    show_validated_popup(self, "Information Validated", "The airport has been validated")
                else:
                    data_info = f"Database Info:\nICAO Code: {self.ids.icao_code.text}, Name: {self.ids.ac_name.text},\nLat: {self.ids.lat.text}, Lon: {self.ids.lon.text}"
                    new_info = f"New Info:\nICAO Code: {icao}, Name: {self.ids.ac_name.text},\nLat: {latitude}, Lon: {longitude}"
                    show_choose_popup(self, "Choose Correct Information", data_info, new_info)
            else:
                show_fail_popup(self, "Failure", "No record\n\nAirport cannot be validated\n\nPlease check your selection")

    def refresh(self):
        self.ids.city_spinner.values = city_names
        self.ids.airport_spinner.values = airport_names
        self.ids.icao_code.text = ""
        self.ids.country.text = ""
        self.ids.ac_name.text = ""
        self.ids.lat.text = ""
        self.ids.lon.text = ""


class UpdateRatingsScreen(Screen):
    def refresh(self):
        self.ids.operator_spinner.values = operator_reviews_names
        self.ids.venue_spinner.values = venue_reviews_names
        self.ids.ratings.text = 'Average Rating: 0\n\nNew Score: 0'

    def update_operator_text(self):
        if self.ids.operator_spinner.text == 'Default':
            self.ids.ratings.text = 'Average Rating: 0\n\nNew Score: 0'
        else:
            query = session.query(Operator).filter(Operator.name == self.ids.operator_spinner.text).one()
            average = query.average_rating
            reviews = query.num_reviews
            reviews_split = reviews.split(",")
            new_review = reviews_split[len(reviews_split)-1]

            self.ids.ratings.text = f"Average Rating: {average}\n\nNew Review: {new_review}"

    def update_venue_text(self):
        if self.ids.venue_spinner.text == 'Default':
            self.ids.ratings.text = 'Average Rating: 0\n\nNew Score: 0'
        else:
            query = session.query(Venue).filter(Venue.name == self.ids.venue_spinner.text).one()
            average = query.average_rating
            reviews = query.reviews
            reviews_split = reviews.split(",")
            new_review = reviews_split[len(reviews_split) - 1]

            self.ids.ratings.text = f"Average Rating: {average}\n\nNew Review: {new_review}"

    def confirm_review(self):
        if self.ids.venue_spinner.text == 'Default' or self.ids.venue_spinner.text == 'Select Venue':
            o_query = session.query(Operator).filter(Operator.name == self.ids.operator_spinner.text).one()
            o_average = o_query.average_rating
            o_reviews = o_query.num_reviews
            o_reviews_split = o_reviews.split(",")
            new_o_review = o_reviews_split[len(o_reviews_split) - 1]
            reviews_total = 0

            for review in o_reviews_split:
                reviews_total += int(review)
            reviews_total += int(new_o_review)

            o_average += float(reviews_total)
            o_average /= float(len(o_reviews_split) + 1)
            o_query.num_reviews += f",{new_o_review}"

            o_query.average_rating = o_average

            session.add(o_query)
            session.commit()
            show_validated_popup(self, "Review Accepted", "Review Accepted")
        elif self.ids.operator_spinner.text == 'Default':
            v_query = session.query(Venue).filter(Venue.name == self.ids.venue_spinner.text).one()
            v_average = v_query.average_rating
            v_reviews = v_query.reviews
            v_reviews_split = v_reviews.split(",")
            new_v_review = v_reviews_split[len(v_reviews_split) - 1]

            v_average = (v_average + new_v_review)/len(v_reviews_split)+1
            v_query.reviews = v_query.reviews + f",{new_v_review}"
            v_query.average_rating = v_average

            session.add(v_query)
            session.commit()
            show_validated_popup(self, "Review Accepted", "Review Accepted")

    def reject_review(self):
        self.ids.ratings.text = 'Average Rating: 0\n\nNew Score: 0'
        show_fail_popup(self, "Review Rejected", 'Review Rejected')


def calculate_distance(location1, location2):
    R = 6371
    lat1, lon1 = map(float, location1.split(','))
    lat2, lon2 = map(float, location2.split(','))

    d = math.acos(math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) +
                  math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                  math.cos(math.radians(lon2 - lon1))) * R
    return d


def city_in_range():
    distance_max = 4000
    for name, coordinate in zip(city_names, city_coords):
        if all(calculate_distance(current_location_coordinate, coord) < distance_max
               for coord in city_coords):
            cities_in_range[name] = coordinate
    return cities_in_range


def city_with_most_activities():
    in_range = city_in_range()
    activities_city = None
    max_activities = 0
    for name, venue_names in in_range:
        activities = 0
        if activities > max_activities:
            max_activities = activities
            activities_city = name, venue_names
    return activities_city


def city_farthest_away():
    in_range = city_in_range()
    farthest_city = None
    max_distance = 0
    for name, coordinate in in_range:
        distance = calculate_distance(current_location_coordinate, coordinate)
        if distance > max_distance:
            max_distance = distance
            farthest_city = name, coordinate
    return farthest_city


def generate_itinerary_1(self):
    itinerary = [past_travel_data]
    next_location = city_with_most_activities()
    departure_date = datetime.now() + timedelta(days=self.days_into_journey)
    arrival_date = departure_date + timedelta(days=1)
    if self.current_location or next_location[0] is NoneType:
        return 'No itinerary can be created'
    itinerary.append({'From': self.current_location, 'to': next_location[0],
                      'departure_date': departure_date, 'arrival_date': arrival_date})
    return itinerary


def generate_itinerary_2(self):
    itinerary = [past_travel_data]
    next_location = city_farthest_away()
    departure_date = datetime.now() + timedelta(days=self.days_into_journey)
    arrival_date = departure_date + timedelta(days=1)
    if self.current_location or next_location[0] is NoneType:
        return 'No itinerary can be created'
    itinerary.append({'From': self.current_location, 'to': next_location[0],
                      'departure_date': departure_date, 'arrival_date': arrival_date})
    return itinerary


class PrepareItineraryScreen(Screen):
    current_location = current_location
    days_into_journey = days_into_journey

    def update_itinerary(self):
        self.ids.itinerary1.text = generate_itinerary_1(self)
        self.ids.itinerary2.text = generate_itinerary_2(self)


class ReviewItineraryScreen(Screen):
    current_location = current_location
    days_into_journey = days_into_journey

    def select_itinerary(self, number_itinerary):
        if number_itinerary is 1:
            self.past_travel_data.append(generate_itinerary_1(self))
            self.days_into_journey = days_into_journey + 1
        else:
            self.past_travel_data.append(generate_itinerary_2(self))
            self.days_into_journey = days_into_journey + 1


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
