import unittest
from unittest.mock import patch, MagicMock
from database import save_conversion, create_tables
from services.currency_converter import convert_currency, convert_currency_from_openapi

class TestDatabase(unittest.TestCase):
    @patch("database.get_db_connection")
    def test_create_tables(self, mock_get_db_connection):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value
        mock_get_db_connection.return_value = mock_connection

        create_tables()

        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("database.get_db_connection")
    def test_save_conversion(self, mock_get_db_connection):
        mock_connection = MagicMock()
        mock_cursor = mock_connection.cursor.return_value
        mock_get_db_connection.return_value = mock_connection

        save_conversion(1, "USD", "EUR", 100, 105.5, 105.7)

        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()


class TestCurrencyConversion(unittest.TestCase):
    @patch("requests.get")
    def test_convert_currency_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rates": {"EUR": 1.2}
        }
        mock_get.return_value = mock_response

        result = convert_currency(100, "USD", "EUR")
        self.assertEqual(result, 120.0)

    @patch("requests.get")
    def test_convert_currency_invalid_amount(self, mock_get):
        with self.assertRaises(ValueError):
            convert_currency(-100, "USD", "EUR")

    @patch("requests.get")
    def test_convert_currency_invalid_currency(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rates": {}
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            convert_currency(100, "USD", "INVALID")

    @patch("requests.get")
    def test_convert_currency_from_openapi_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "usd": {"eur": 1.2}
        }
        mock_get.return_value = mock_response

        result = convert_currency_from_openapi(100, "USD", "EUR")
        self.assertEqual(result, 120.0)

    @patch("requests.get")
    def test_convert_currency_from_openapi_invalid_amount(self, mock_get):
        with self.assertRaises(ValueError):
            convert_currency_from_openapi(-100, "USD", "EUR")

    @patch("requests.get")
    def test_convert_currency_from_openapi_invalid_currency(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "usd": {}
        }
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            convert_currency_from_openapi(100, "USD", "INVALID")

if __name__ == "__main__":
    unittest.main()