from kivy.app import App
from kivy.core.window import Window
from kivy.modules import inspector
from kivy.uix.screenmanager import Screen

from database import FinalDatabase


class StartUpScreen(Screen):
    pass


class LoadingScreen(Screen):
    pass


class MainMenuScreen(Screen):
    pass


class ValidateLocationsScreen(Screen):
    pass


class UpdateRatingsScreen(Screen):
    pass


class PrepareItineraryScreen(Screen):
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
