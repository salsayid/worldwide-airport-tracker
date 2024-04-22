import json
from datetime import datetime, date, timedelta


from sys import stderr

import sqlalchemy
import requests
from kivy.app import App
from kivy.core.text import Label
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen, ScreenManager
from pip._internal.network import session
from sqlalchemy.exc import SQLAlchemyError

from database import FinalDatabase

class MainScreen(Screen):
    pass

class TravelPlannerApp(App):
    def build(self):
        inspector.create_inspector(Window, self)  # For inspection (press control-e to toggle).

if __name__ == '__main__':
    url = FinalDatabase.construct_mysql_url('localhost', 3306, 'name', 'username', 'password')
    milestone_1_database = FinalDatabase(url)
    session = milestone_1_database.create_session()
    app = TravelPlannerApp()
    app.run()