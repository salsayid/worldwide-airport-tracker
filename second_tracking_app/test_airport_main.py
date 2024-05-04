import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from datetime import datetime
from second_tracking_app.airport_installer import AirportApp

class TestAirportApp(unittest.TestCase):
    @patch('builtins.input', side_effect=['1', 'Airport Name', 'ABC',
                                          'Location', '2', 'City Name', 'Entity', 'Location', '3', 'ABC', '2024-05-03'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_main_function(self, mock_stdout, mock_input):
        app = AirportApp()
        app.build()

        output = mock_stdout.getvalue()
        self.assertIn("Airport added successfully!", output)
        self.assertIn("City added successfully!", output)
        self.assertIn("Forecast for ABC on 2024-05-03:", output)

if __name__ == '__main__':
    unittest.main()