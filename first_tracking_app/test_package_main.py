import unittest
from unittest.mock import MagicMock, patch, Mock
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, MetaData, Table
from package_main import SubmitReviewScreen
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from installer.database import FinalDatabase, Forecast, Operator, Venue

class TestSubmitReviewScreen(unittest.TestCase):
    def setUp(self):
        self.screen = SubmitReviewScreen()
        self.screen.ids = MagicMock()
        self.screen.ids.existing_operator_name = Mock()
        self.screen.ids.operator_review = Mock()

        self.db = FinalDatabase(FinalDatabase.construct_in_memory_url())
        self.session = self.db.session

        Operator.__table__.create(bind=self.db.engine, checkfirst=True)
        Venue.__table__.create(bind=self.db.engine, checkfirst=True)



        self.operator = Operator(name='Test Operator')
        self.session.add(self.operator)
        self.session.commit()

    @patch('package_main.session', new_callable=lambda: self.session)
    def test_addOperatorReview(self, mock_session):
        self.screen.ids.existing_operator_name.text = 'Test Operator'
        self.screen.ids.operator_review.text = '5'

        self.screen.addOperatorReview()

        self.assertEqual(self.operator.reviews, '5')
        self.assertEqual(self.operator.average_rating, 5.0)

if __name__ == '__main__':
    unittest.main()