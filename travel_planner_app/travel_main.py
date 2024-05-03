from kivy.app import App
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.uix.screenmanager import Screen

from database import FinalDatabase


class StartUpScreen(Screen):
    def submit_credentials(self):
        try:
            url = FinalDatabase.construct_mysql_url(self.ids.authority.text, int(self.ids.port_number.text), self.ids.database_name.text, self.ids.database_username.text, self.ids.database_password.text)
            self.operator_database = FinalDatabase(url)
            self.session = self.operator_database.create_session()
        except SQLAlchemyError as exception:
            print(exception)


class LoadingScreen(Screen):
    pass


class MainMenuScreen(Screen):
    pass


class ValidateLocationsScreen(Screen):
    pass


class UpdateRatingsScreen(Screen):
    pass


class PrepareItineraryScreen(Screen):
    current_location = StringProperty('Lincoln, Nebraska')
    days_into_journey = NumericProperty(0)

    def update_info(self, location, day):
        self.current_location = location
        self.days_into_journey = day



    def calculate_distance(self, location1, location2):
        R = 6371
        lat1, lon1 = location1['latitude'], location1['longitude']
        lat2, lon2 = location2['latitude'], location2['longitude']
        d = math.acos(math.sin(math.radians(lat1)) * math.sin(math.radians(lat2)) +
                      math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
                      math.cos(math.radians(lon2 - lon1))) * R
        return d

    def _get_forecast(self, location, date_str):
        api_key = "b35d2791970e14588d0fcdb917c4c7ff"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}"
        try:
            response = requests.get(url)
            data = response.json()
            if response.status_code == 200:
                forecast = data["weather"][0]["description"]
                print(f"Forecast for {location} on {date_str}: {forecast}")
                return forecast
            else:
                print(f"Failed to fetch forecast. Status code: {response.status_code}")
                return None
        except Exception as e:
            print("An error occurred:", e)
            return None
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

    def generate_itinerary_1(self, current_location, past_travel_data):
        itinerary = [past_travel_data]
        next_location = self.city_farthest_away()
        arrival_date = datetime.now() + timedelta(days=1)
        itinerary.append({'from': current_location['name'], 'to': next_location['name'],
                          'departure_date': datetime.now(), 'arrival_date': arrival_date})
        return itinerary
    def generate_itinerary_2(self, current_location, past_travel_data):
        itinerary = [past_travel_data]
        next_location = self.city_with_most_activities()
        arrival_date = datetime.now() + timedelta(days=1)
        itinerary.append({'from': current_location['name'], 'to': next_location['name'],
                          'departure_date': datetime.now(), 'arrival_date': arrival_date})
        return itinerary

class ReviewItineraryScreen(Screen):
    pass

class TravelPlannerApp(App):
    def build(self):
        inspector.create_inspector(Window, self)  # For inspection (press control-e to toggle).


if __name__ == '__main__':
    url = FinalDatabase.construct_mysql_url('localhost', 3306, 'name', 'username', 'password')
    final_database = FinalDatabase(url)
    session = final_database.create_session()
    app = TravelPlannerApp()
    app.run()
