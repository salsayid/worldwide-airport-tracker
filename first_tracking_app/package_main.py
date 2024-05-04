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
                    self.create_venue(venue_name, venue_lat, venue_lon, venue_type)
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

    #TODO Test
    def create_venue(self, name, latitude, longitude, type):
        venue = Venue(name=name, latitude=latitude, longitude=longitude, type=type)
        session.add(venue)
        session.commit()

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
                    self.create_operator(operator_name, operator_rating)
                except SQLAlchemyError as exception:
                    show_popup(self, 'Failed', f'Failed to create new operator!\nCause: {exception}')
                else:
                    show_popup(self, 'Success', 'New operator created!')
                    self.ids.operator_name.text = ''
                    self.ids.operator_rating.text = ''
                    
    def clearAddOperatorFields(self):
        self.ids.operator_name.text = ''
        self.ids.operator_rating.text = ''
    
    #TODO Test
    def create_operator(self, name, rating):
        operator = Operator(name=name, average_rating=rating)
        session.add(operator)
        session.commit()

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
                    self.edit_operator(existing_operator, new_operator_name, operator_rating)
                    
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
        
    #TODO Test
    def edit_operator(self, existing_operator, new_operator_name, operator_rating):
        existing_operator.name = new_operator_name
        existing_operator.average_rating = operator_rating
        session.commit()

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
        #print(today)
        next_5_days = [today + timedelta(days=i) for i in range(0, 5)]
        date_formatted_5_days = []
        for day in next_5_days:
            for hour in range(0, 24, 3):  # Change the step size to 3
                time_code = f"{hour:02d}:00:00"
                date_formatted_5_days.append(f"{day.strftime('%Y-%m-%d')} {time_code}")
        return date_formatted_5_days


    #Forecast       
    def get_forecast(self, lat, lon):
        try:
            parent_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            file_path = os.path.join(parent_directory, "installer", "credentials.json")
            with open(file_path, 'r') as file:
                credential_information = json.load(file)
            api_key = credential_information['API_KEY']
        except FileNotFoundError:
            show_popup(self, 'Failed', 'Could not find credentials.json file!')
            exit(1)


        url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}"
        try:
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                weather = None
            
                for item in data['list']:
                    #print (item['dt_txt'])
                    if item['dt_txt'] == self.ids.date_for_forecast.text:
                        weather = item['weather'][0]['description']
                        break
        
                return weather
                
            else:
                show_popup(self, 'Failed', f'Failed to fetch forecast. Status code: {response.status_code}')
            
        except Exception as e:
            show_popup(self, 'Failed', f'An error occurred: {e}')
    
    def getWeather(self):
        try:
            try:
                venue_name = self.ids.existing_venue_name.text
                venues = session.query(Venue).all()
                current_venue = None
                for venue in venues:
                    venue_info = f"Name: {venue.name} | Location: {venue.latitude}, {venue.longitude} | Type: {venue.type}"
                    if venue_info == venue_name:
                        current_venue = venue
                        break
                    
                existing_venue = session.query(Venue).filter_by(name=current_venue.name).first()
            except SQLAlchemyError as exception:
                    show_popup(self, 'Failed', f'Failed to get venue information!\nCause: {exception}')
                
            lat = existing_venue.latitude
            long = existing_venue.longitude

            weather_result = self.get_forecast(lat, long)
            
            if weather_result is None:
                show_popup(self, 'No Information', 'The selected time does not have any weather information.')
            else:
                show_popup(self, 'Weather Result', f'The weather for the selected time is: {weather_result}')
                self.save_to_database(current_venue, weather_result, self.ids.date_for_forecast.text)
                
        
        except Exception as e:
            show_popup(self, 'Failed', f'Failed to get venue location!\nCause: {e}')
    

    #TODO Test
    def save_to_database(self, current_venue, weather_result, date):
        try:
            forecast = Forecast(date=date, forecastData=weather_result, venueID=current_venue.venueID)
            session.add(forecast)
            session.commit()
        except SQLAlchemyError as exception:
            show_popup(self, 'Failed', f'Failed to save forecast to database!\nCause: {exception}')
        else:
            show_popup(self, 'Success', 'Forecast saved to database!')
            

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
                    
                    if existing_operator.num_reviews is not None:
                        review_list = existing_operator.num_reviews.split(',')
                        review_list.append(operator_review)
                        existing_operator.num_reviews = ','.join(review_list)
                        
                        average_rating = 0
                        for review in review_list:
                            average_rating += int(review[0])
                            #print (average_rating)
                            
                        existing_operator.average_rating = average_rating / len(review_list)
                    else:
                        existing_operator.num_reviews = operator_review
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
                            #print (average_rating)
                            
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