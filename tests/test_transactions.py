import unittest
from website import transactions
from unittest.mock import patch

class TransactionsTestCase(unittest.TestCase):
    @patch('website.transactions.day_max_deposit_limit_reached')
    @patch('website.transactions.day_max_deposit_frequency_reached')
    def test_valid_deposit(self, mock_max_frequency, mock_max_limit):
        #valid deposit with amount less than 40000
        self.assertTrue(transactions.valid_deposit(1, "deposit", "30000"))

        #valid deposit with amount equal to 40000
        self.assertTrue(transactions.valid_deposit(1, "deposit", "40000"))

        #invalid deposit with amount greater than 40000
        with self.assertRaises(ValueError):
            transactions.valid_deposit(1, "deposit", "45000")

        #invalid deposit with max daily deposit limit reached
        mock_max_limit.return_value = True
        self.assertFalse(transactions.valid_deposit(1, "deposit", "20000"))

        #invalid deposit with max deposit frequency limit reached
        mock_max_frequency.return_value = True
        self.assertFalse(transactions.valid_deposit(1, "deposit", "20000"))


if __name__ == '__main__':
    unittest.main()