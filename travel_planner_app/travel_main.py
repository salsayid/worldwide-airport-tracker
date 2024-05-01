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
