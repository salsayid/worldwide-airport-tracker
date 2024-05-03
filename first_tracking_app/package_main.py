# Standard library imports
from datetime import date, datetime, timedelta
from json import dumps, loads
from sys import stderr
import os
import sys
import json

# Third party imports
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.modules import inspector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from sqlalchemy.exc import SQLAlchemyError
import requests

# Local application imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from installer.database import FinalDatabase, Forecast, Operator, Venue


def show_popup(self, happened, message):
    content = BoxLayout(orientation='vertical')
    label = Label(text=message, font_size=20, size_hint=(1, 0.8), text_size=(400, None), halign='center', valign='middle')
    close_button = Button(text='Close', size_hint=(1, 0.2))
    content.add_widget(label)
    content.add_widget(close_button)
    popup = Popup(title=happened, content=content, size_hint=(None, None), size=(400, 200))
    close_button.bind(on_release=popup.dismiss)
    popup.open()

class MainScreen(Screen):
    def exit_program(self):
        App.get_running_app().stop()

class NewVenueScreen(Screen):
    def createNewVenue(self):
        venue_name = self.ids.venue_name.text.strip()
        venue_lat = self.ids.venue_lat.text.strip()
        venue_lon = self.ids.venue_lon.text.strip()
        venue_type = self.ids.venue_type.text.strip()

        if venue_name == '' or venue_lat == '' or venue_lon == '' or venue_type == '':
            show_popup(self, 'Failed', 'Failed to create new venue!\nCause: All fields must be filled.')
        else:
            existing_venue = session.query(Venue).filter_by(name=venue_name, latitude=venue_lat, longitude=venue_lon, type=venue_type).first()
            if existing_venue:
                show_popup(self, 'Failed', 'Failed to create new venue!\nCause: Venue with the same name, location, and type already exists.')
            else:
                try:
                    new_venue = Venue(name=venue_name, latitude=venue_lat, longitude=venue_lon, type=venue_type)
                    session.add(new_venue)
                    session.commit()
                except SQLAlchemyError as exception:
                    show_popup(self, 'Failed', f'Failed to create new venue!\nCause: {exception}')
                else:
                    show_popup(self, 'Success', 'New venue created!')
                    self.ids.venue_name.text = ''
                    self.ids.venue_lat.text = ''
                    self.ids.venue_lon.text = ''
                    self.ids.venue_type.text = 'Type Of Venue'
                    
    def clearNewVenueFields(self):
        self.ids.venue_name.text = ''
        self.ids.venue_lat.text = ''
        self.ids.venue_lon.text = ''
        self.ids.venue_type.text = 'Type Of Venue'

class AddEditOperatorScreen(Screen):
    pass

class AddOperatorScreen(Screen):
    def createNewOperator(self):
        operator_name = self.ids.operator_name.text.strip()
        operator_rating = self.ids.operator_rating.text.strip()

        if operator_name == '' or operator_rating == '':
            show_popup(self, 'Failed', 'Failed to create new operator!\nCause: All fields must be filled.')
        else:
            existing_operator = session.query(Operator).filter_by(name=operator_name).first()
            if existing_operator:
                show_popup(self, 'Failed', f'Failed to create new operator!\nCause: Operator with the same name already exists.')
            else:
                try:
                    new_operator = Operator(name=operator_name, average_rating=operator_rating)
                    session.add(new_operator)
                    session.commit()
                except SQLAlchemyError as exception:
                    show_popup(self, 'Failed', f'Failed to create new operator!\nCause: {exception}')
                else:
                    show_popup(self, 'Success', 'New operator created!')
                    self.ids.operator_name.text = ''
                    self.ids.operator_rating.text = ''
                    
    def clearAddOperatorFields(self):
        self.ids.operator_name.text = ''
        self.ids.operator_rating.text = ''

class EditOperatorScreen(Screen):
    def editExistingOperator(self):
        operator_name = self.ids.existing_operator_name.text.strip()
        new_operator_name = self.ids.new_operator_name.text.strip()
        operator_rating = self.ids.new_operator_rating.text.strip()

        if operator_name == '' or new_operator_name == '' or operator_rating == '':
            show_popup(self, 'Failed', 'Failed to edit operator!\nCause: All fields must be filled.')
        else:
            existing_operator = session.query(Operator).filter_by(name=operator_name).first()
            if not existing_operator:
                show_popup(self, 'Failed', f'Failed to edit operator!\nCause: Operator does not exist.')
            else:
                try:
                    existing_operator.name = new_operator_name
                    existing_operator.average_rating = operator_rating
                    session.commit()
                except SQLAlchemyError as exception:
                    show_popup(self, 'Failed', f'Failed to edit operator!\nCause: {exception}')
                else:
                    show_popup(self, 'Success', 'Operator edited!')
                    self.ids.existing_operator_name.text = "Existing Operator's Name"
                    self.ids.new_operator_name.text = ''
                    self.ids.new_operator_rating.text = ''
                    self.ids.existing_operator_name.values = self.getOperatorNames()

    def getOperatorNames(self):
        operator_names = []
        operators = session.query(Operator).all()
        for operator in operators:
            operator_names.append(operator.name)
        return operator_names
    
    
    def updateSpinner(self):
        self.ids.existing_operator_name.values = self.getOperatorNames()

    def clearEditOperatorFields(self):
        self.ids.existing_operator_name.text = "Existing Operator's Name"
        self.ids.new_operator_name.text = ''
        self.ids.new_operator_rating.text = ''

#TODO
class CheckForecastScreen(Screen):
    def getVenueNames(self):
        venue_names = []
        venues = session.query(Venue).all()
        for venue in venues:
            venue_info = f"Name: {venue.name} | Location: {venue.latitude}, {venue.longitude} | Type: {venue.type}"
            venue_names.append(venue_info)
        return venue_names
    
    def updateSpinner(self):
        self.ids.existing_venue_name.values = self.getVenueNames()

    def generateNext7Days(self):
        today = date.today()
        next_7_days = [today + timedelta(days=i) for i in range(0, 7)]
        date_formatted_7_days = []
        for day in next_7_days:
            date_formatted_7_days.append(day.strftime("%Y/%m/%d"))
        return date_formatted_7_days


    #Forecast    
    '''   
    def get_forecast(self):
        
       # api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API key}
        
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
    
    
    
    def settupGetWeather(self):
        try:
            existing_venue_name = self.ids.existing_venue_name.text
            location = existing_venue_name.split('\nLocation: ')[1].split(', ')
            venue_lat = location[0]
            venue_lon = location[1].split('\nType: ')[0]
            self.getWeather(venue_lat, venue_lon)
        except Exception as e:
            show_popup(self, 'Failed', f'Failed to get venue location!\nCause: {e}')
    
    
    def getWeather(self, lat, lon):
        connection = RESTConnection('api.openweathermap.org', 443, '/data/2.5')
        connection.send_request(
            'forecast',
            {
                'appid': cred.API_KEY,
                'lat': lat,
                'lon': lon,
                'units': 'imperial'
            },
            None,
            self.store_forecast_data,
            self.connectionFailed,
            None
        )

    def connectionFailed(self, _, response):
        show_popup(self, 'Failed', 'Failed to connect to weather API!')


    def store_forecast_data(self, _, response):
        #print (response)
        if response:
            try:
                existing_venue_name = self.ids.existing_venue_name.text
                location = existing_venue_name.split('\nLocation: ')[1].split(', ')
                venue_lat = location[0]
                venue_lon = location[1].split('\nType: ')[0]
                
                test_response = (response)
                
                print (test_response)
                
                #chosen_date = self.ids.date_for_forecast.text
 
                #print (self.parseWeather(response))
 
 
                self.ids.forecast_label.text = ('Forecast added to database')
                
                
            except Exception as e:
                print(e)
                    
            
            
    def parseWeather(self, forecast_data):
        # Assuming `data` is your JSON string
        data = json.loads(data)

        # Convert the date string to a datetime object for comparison
        target_date = datetime.strptime('2024-04-17 03:00:00', '%Y-%m-%d %H:%M:%S')

        for item in data['list']:
            # Convert the timestamp to a datetime object
            item_date = datetime.fromtimestamp(item['dt'])

            if item_date == target_date:
                print(f"Temperature: {item['main']['temp']}°F")
                print(f"Humidity: {item['main']['humidity']}%")
                print(f"Wind Speed: {item['wind']['speed']} mph")
                print(f"Weather Description: {item['weather'][0]['description']}")
                break


        
    def save_to_database(self):
        try:
            new_forecast = Forecast(date=self.date, temperature=self.temperature, humidity=self.humidity,
                                    wind_speed=self.wind_speed, weather_description=self.weather_description)
            session.add(new_forecast)
            session.commit()
        except SQLAlchemyError as exception:
            show_popup(self, 'Failed', f'Failed to save forecast to database!\nCause: {exception}')
        else:
            show_popup(self, 'Success', 'Forecast saved to database!')
            
    '''

class SubmitReviewScreen(Screen):
    
    def getOperatorNames(self):
        operator_names = []
        operators = session.query(Operator).all()
        for operator in operators:
            operator_names.append(operator.name)
        return operator_names
    
    def getVenueNames(self):
        venue_names = []
        venues = session.query(Venue).all()
        for venue in venues:
            venue_info = f"Name: {venue.name} | Location: {venue.latitude}, {venue.longitude} | Type: {venue.type}"
            venue_names.append(venue_info)
        return venue_names
    
    def updateSpinner(self):
        self.ids.existing_operator_name.values = self.getOperatorNames()
        self.ids.existing_venue_name.values = self.getVenueNames()
        
    def clearReviewFields(self):
        self.ids.existing_operator_name.text = "Existing Operator's Name"
        self.ids.existing_venue_name.text = "Existing Venue's Name"
        self.ids.venue_review.text = ''
        self.ids.operator_review.text = ''

    def addOperatorReview(self):
        try:
            operator_name = self.ids.existing_operator_name.text
            operator_review = self.ids.operator_review.text
            
            if operator_name == '' or operator_review == '':
                show_popup(self, 'Failed', 'Failed to add operator review!\nCause: All fields must be filled.')
            else:
                try:
                    existing_operator = session.query(Operator).filter_by(name=operator_name).first()
                    
                    if existing_operator.reviews is not None:
                        review_list = existing_operator.reviews.split(',')
                        review_list.append(operator_review)
                        existing_operator.reviews = ','.join(review_list)
                        
                        average_rating = 0
                        for review in review_list:
                            average_rating += int(review[0])
                            print (average_rating)
                            
                        existing_operator.average_rating = average_rating / len(review_list)
                    else:
                        existing_operator.reviews = operator_review
                    session.commit()
                except SQLAlchemyError as exception:
                    show_popup(self, 'Failed', f'Failed to add operator review!\nCause: {exception}')
                else:
                    show_popup(self, 'Success', 'Operator review added!')
                    self.ids.existing_operator_name.text = "Existing Operator's Name"
                    self.ids.operator_review.text = ''
        except Exception as e:
            show_popup(self, 'Failed', f'Failed to add operator review!\nCause: {e}')
            self.ids.existing_operator_name.text = "Existing Operator's Name"
            self.ids.operator_review.text = ''
                
    def addVenueReview(self):
        try:
            venue_name = self.ids.existing_venue_name.text
            venue_review = self.ids.venue_review.text

            if venue_name == '' or venue_review == '':
                show_popup(self, 'Failed', 'Failed to add venue review!\nCause: All fields must be filled.')
            else:
                try:
                    venues = session.query(Venue).all()
                    current_venue = None
                    for venue in venues:
                        venue_info = f"Name: {venue.name} | Location: {venue.latitude}, {venue.longitude} | Type: {venue.type}"
                        if venue_info == venue_name:
                            current_venue = venue
                            break
                        
                    existing_venue = session.query(Venue).filter_by(name=current_venue.name).first()
                    
                    if existing_venue.reviews is not None:
                        review_list = existing_venue.reviews.split(',')
                        review_list.append(venue_review)
                        existing_venue.reviews = ','.join(review_list)
                        
                        average_rating = 0
                        for review in review_list:
                            average_rating += int(review[0])
                            print (average_rating)
                            
                        existing_venue.average_rating = average_rating / len(review_list)
                    else:
                        existing_venue.reviews = venue_review
                    session.commit()
                except SQLAlchemyError as exception:
                    show_popup(self, 'Failed', f'Failed to add venue review!\nCause: {exception}')
                else:
                    show_popup(self, 'Success', 'Venue review added!')
                    self.ids.existing_venue_name.text = "Existing Venue's Name"
                    self.ids.venue_review.text = ''
        except Exception as e:
            show_popup(self, 'Failed', f'Failed to add venue review!\nCause: {e}')
            self.ids.existing_venue_name.text = "Existing Venue's Name"
            self.ids.venue_review.text = ''
            



#^ MAIN RUNNER

class PackageDealApp(App):
    def build(self):
        inspector.create_inspector(Window, self)  # For inspection (press control-e to toggle).

if __name__ == '__main__':
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
    
    url = FinalDatabase.construct_mysql_url(authority, port, database_name, username, password)
    package_deal_db = FinalDatabase(url)
    session = package_deal_db.create_session()
    app = PackageDealApp()
    app.run()