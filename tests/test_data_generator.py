#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for Large Test Data Generator.
"""
import unittest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from src.large_test_data_generator.data_generator import (
    is_valid_card, random_date_between, create_row
)


class TestDataGenerator(unittest.TestCase):
    """Test case for the data generator module."""

    def test_is_valid_card(self):
        """Test credit card validation using Luhn algorithm."""
        # Test valid card numbers
        self.assertTrue(is_valid_card("4532015112830366"))  # Visa
        self.assertTrue(is_valid_card("5425233430109903"))  # Mastercard
        self.assertTrue(is_valid_card("4485275742308327"))  # Visa
        
        # Test invalid card numbers
        self.assertFalse(is_valid_card("4532015112830367"))  # Invalid Visa
        self.assertFalse(is_valid_card("1234567890123456"))  # Random invalid
    
    def test_random_date_between(self):
        """Test random date generation between two dates."""
        start = "01.JAN.2000 00:00:00"
        end = "31.DEC.2020 23:59:59"
        date_format = "%d.%b.%Y %H:%M:%S"
        
        # Test with prop = 0 (should be start date)
        result = random_date_between(start, end, date_format, 0)
        self.assertEqual(result, "01.Jan.2000 00:00:00")
        
        # Test with prop = 1 (should be end date)
        result = random_date_between(start, end, date_format, 1)
        self.assertEqual(result, "31.Dec.2020 23:59:59")
        
        # Test with prop = 0.5 (should be between)
        result = random_date_between(start, end, date_format, 0.5)
        self.assertNotEqual(result, start)
        self.assertNotEqual(result, end)
    
    @patch('src.large_test_data_generator.data_generator.random.randrange')
    @patch('src.large_test_data_generator.data_generator.random.choice')
    @patch('src.large_test_data_generator.data_generator.random.random')
    def test_create_row(self, mock_random_random, mock_choice, mock_randrange):
        """Test row creation with mocked random functions."""
        mock_choice.side_effect = lambda x: x[0]
        mock_random_random.return_value = 0.5
        mock_randrange.return_value = 42
        
        # Create test data
        column_definitions = [
            {"datatype": "string", "is_variable_legth": False, "is_null": False, "length": 5},
            {"datatype": "number", "min_range": "1", "max_range": "2"},
        ]
        separator = ","
        country_array = ["US", "CA"]
        phone_array = []
        my_file = {}
        
        # Test create_row
        result = create_row(column_definitions, separator, country_array, phone_array, my_file)

        # Verify results
        self.assertEqual(result, '"aaaaa","42"')


if __name__ == "__main__":
    unittest.main()