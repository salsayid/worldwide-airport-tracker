import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import sys, os
from sys import stderr
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from installer.database import FinalDatabase, Forecast, Operator, Venue
from first_tracking_app.package_main import SubmitReviewScreen

def setup():
    try:
        url = FinalDatabase.construct_in_memory_url()
        test_db = FinalDatabase(url)
        test_db.drop_all_tables()
        test_db.ensure_package_deal_tables_exist()
        print('Tables created.')
        session = test_db.create_session()
        add_starter_data(session)
        session.commit()
        print('Records created.')
    
    except SQLAlchemyError as e:
        print('Database setup failed!', file=stderr)
        print(f'Cause: {e}', file=stderr)
        exit(1)

def add_starter_data(session):
    #Package Deal App
    operator1 = Operator(name='Test Jeffery Danger', average_rating=5)
    session.add(operator1)

    operator2 = Operator(name='Test Stephan Hawkson', average_rating=5, reviews='3,4,5,6,7')
    session.add(operator2)
    
    operator3 = Operator(name='Test John Doe', average_rating=5, reviews='3,4,5,6,7')
    session.add(operator3)

    restaurant = Venue(name=' Test Indoor Restaurant', latitude='40.8207', longitude='-96.7005',
                    type='Indoor Restaurant', operators=[operator1])
    session.add(restaurant)

    theater = Venue(name='Test Indoor Theater', latitude='40.8207', longitude='-96.7005', type='Indoor Theater',
                    operators=[operator1, operator2], average_rating=4.5, reviews='3,4,5,6,7')
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

class TestSubmitReviewScreen(unittest.TestCase):
    @patch('first_tracking_app.package_main.session')
    @patch('first_tracking_app.package_main.show_popup')
    def test_addOperatorReview(self, mock_show_popup, mock_session):
        # Arrange
        screen = SubmitReviewScreen()
        screen.ids = {
            'existing_operator_name': MagicMock(text='Test Operator'),
            'operator_review': MagicMock(text='5')
        }
        mock_operator = MagicMock(reviews=None)
        mock_session.query().filter_by().first.return_value = mock_operator

        # Act
        screen.addOperatorReview()

        # Assert
        mock_session.commit.assert_called_once()
        mock_show_popup.assert_called_once_with(screen, 'Success', 'Operator review added!')
        self.assertEqual(screen.ids['existing_operator_name'].text, "Existing Operator's Name")
        self.assertEqual(screen.ids['operator_review'].text, '')

if __name__ == '__main__':

    setup()
    unittest.main()
    
    