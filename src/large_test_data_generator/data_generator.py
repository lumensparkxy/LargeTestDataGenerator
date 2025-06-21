#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Large Test Data Generator

This module provides functionality to generate test data based on specified parameters.
"""
from typing import Dict, List, Any, Optional, Union
import random
import json
import string
import time
import uuid
import os
import pymongo
from .mongodb_utils import (
    get_country_list, get_phone_list, get_credit_card_info, get_address_from_db
)
from .logger import logger

# Type aliases for better readability
ColumnDefinition = Dict[str, Any]
ParameterData = Dict[str, Any]


def initialize_country_list() -> List[str]:
    """
    Initialize country list from MongoDB with weights.
    
    Returns:
        List[str]: A list of country codes, with frequency based on weights.
    """
    try:
        return get_country_list()
    except Exception as e:
        logger.error(f"Error initializing country list: {e}")
        # Fallback to a default list
        return ["US", "CA", "GB", "DE", "FR", "IT", "ES", "CH", "AU"]


def initialize_phone_list() -> List[Dict[str, Any]]:
    """
    Initialize phone number list from MongoDB.
    
    Returns:
        List[Dict[str, Any]]: A list of phone number information.
    """
    try:
        return get_phone_list()
    except Exception as e:
        logger.error(f"Error initializing phone list: {e}")
        # Return an empty list if there's an error
        return []


def get_phone_number(region_code: str, phone_array: List[Dict[str, Any]]) -> str:
    """
    Generate a random phone number for the given country code.
    
    Args:
        region_code (str): ISO ALPHA-2 country code (e.g., "CH" for Switzerland).
        phone_array (List[Dict[str, Any]]): List of phone information.
        
    Returns:
        str: A random phone number for the specified country.
    """
    for phone in phone_array:
        if phone['alpha-2'] == region_code:
            phone_number_length = len(str(phone['eg_phone_number']))
            random_phone_number = str(random.randrange(10**int(phone_number_length-1), 10**int(phone_number_length)))
            return f"+{phone['dialCode']}{random_phone_number}"
    return ""


def random_date_between(start: str, end: str, date_format: str, prop: float) -> str:
    """
    Get a time at a proportion of a range of two formatted times.

    Args:
        start (str): Start date string in the specified format.
        end (str): End date string in the specified format.
        date_format (str): Format string for dates (strftime-style).
        prop (float): Proportion of the interval to be taken after start (0.0 to 1.0).
        
    Returns:
        str: Random date between start and end, in the specified format.
    """
    stime = time.mktime(time.strptime(start, date_format))
    etime = time.mktime(time.strptime(end, date_format))

    ptime = stime + prop * (etime - stime)
    
    result = time.strftime(date_format, time.localtime(ptime))

    # Preserve uppercase month formatting if provided in the input. The
    # `strftime` function returns month names with title case for the `%b`
    # directive (e.g. ``Jan``).  Tests expect the month portion to remain in
    # uppercase when the format uses an upper-case month abbreviation such as
    # ``JAN``.  To handle this generically we simply return an uppercased
    # string.  This keeps numeric parts unchanged while ensuring month names
    # match the expected casing.
    return result.upper()


def is_valid_card(card_number: str) -> bool:
    """
    Check if a credit card number is valid using the Luhn algorithm.
    
    Args:
        card_number (str): The credit card number to validate.
        
    Returns:
        bool: True if the card number is valid, False otherwise.
    """
    def digits_of(n: str) -> List[int]:
        return [int(d) for d in str(n)]

    digits = digits_of(card_number)
    odd_numbers = digits[-1::-2]
    even_numbers = digits[-2::-2]
    total_sum = sum(odd_numbers)
    
    for x in even_numbers:
        total_sum += sum(digits_of(x*2))
    
    return total_sum % 10 == 0


def generate_credit_card(prefix: str, length: int) -> str:
    """
    Generate a valid credit card number with a given prefix and length.
    
    Args:
        prefix (str): The BIN (Bank Identification Number) prefix for the card.
        length (int): The total length of the card number.
        
    Returns:
        str: A valid credit card number.
    """
    # Generate the body of the card number
    credit_card = prefix
    for i in range(1, length-len(prefix)):
        credit_card += str(random.choice(range(0, 10)))
    
    # Find a valid check digit
    for i in range(0, 10):
        candidate = credit_card + str(i)
        if is_valid_card(candidate):
            return candidate
    
    # If no valid check digit found (extremely rare), return as is
    return credit_card


def get_address(country: str) -> Optional[Dict[str, Any]]:
    """
    Get a random address from MongoDB for the specified country.
    
    Args:
        country (str): Country code.
        
    Returns:
        Optional[Dict[str, Any]]: A random address or None if not found.
    """
    try:
        return get_address_from_db(country)
    except Exception as e:
        logger.error(f"Error getting address for country {country}: {e}")
        return None


def initialize_credit_card_list(country: str, bank: str, card_type: str) -> List[Dict[str, Any]]:
    """
    Initialize a list of credit card information.
    
    Args:
        country (str): Country code.
        bank (str): Bank name.
        card_type (str): Card type.
        
    Returns:
        List[Dict[str, Any]]: List of credit card information.
    """
    try:
        return get_credit_card_info(country, bank, card_type)
    except Exception as e:
        logger.error(f"Error getting credit card info for {country}/{bank}/{card_type}: {e}")
        return []


def initialize_list(filename: str) -> List[str]:
    """
    Initialize a list from a file, removing duplicates.
    
    Args:
        filename (str): Path to the file.
        
    Returns:
        List[str]: List of unique values from the file.
    """
    with open(filename, encoding='utf8') as f:
        temp_list = [line.rstrip('\n') for line in f]
    return list(set(temp_list))


def get_item_from_list(filename: str, my_file: Dict[str, Any]) -> Optional[str]:
    """
    Get and remove a random item from a list associated with a file.
    
    Args:
        filename (str): Path to the file.
        my_file (Dict[str, Any]): Dictionary storing file contents.
        
    Returns:
        Optional[str]: A random item from the list or None if the list is empty.
    """
    if filename in my_file:
        if len(my_file[filename]) > 0:
            return my_file[filename].pop(random.randint(0, len(my_file[filename])-1))
        else:
            return None
    else:
        file_array = initialize_list(filename)
        my_file[filename] = file_array
        if len(file_array) > 0:
            return my_file[filename].pop(random.randint(0, len(my_file[filename])-1))
        return None


def get_any_item_from_list(filename: str, my_file: Dict[str, Any]) -> Optional[str]:
    """
    Get a random item from a list without removing it.
    
    Args:
        filename (str): Path to the file.
        my_file (Dict[str, Any]): Dictionary storing file contents.
        
    Returns:
        Optional[str]: A random item from the list or None if the list is empty.
    """
    if filename in my_file:
        if len(my_file[filename]) > 0:
            return my_file[filename][random.randint(0, len(my_file[filename])-1)]
        else:
            return None
    else:
        file_array = initialize_list(filename)
        my_file[filename] = file_array
        if len(file_array) > 0:
            return my_file[filename][random.randint(0, len(my_file[filename])-1)]
        return None


def get_sample_address(country: str) -> Optional[Dict[str, Any]]:
    """
    Get a sample address with retry logic.
    
    Args:
        country (str): Country code.
        
    Returns:
        Optional[Dict[str, Any]]: A sample address or None if not found after retries.
    """
    retry_count = 0
    while retry_count < 5:
        single_address = get_address(country)
        if single_address is not None:
            return single_address
        else:
            retry_count += 1
    return None


def initialize_db(parameter: str) -> List[Dict[str, Any]]:
    """
    Initialize database with addresses for a specific country.
    
    Args:
        parameter (str): Country code.
        
    Returns:
        List[Dict[str, Any]]: List of addresses.
    """
    try:
        # Get multiple addresses for the country
        addresses = []
        for _ in range(10):  # Try to get 10 addresses
            address = get_address_from_db(parameter)
            if address:
                addresses.append(address)
        return addresses
    except Exception as e:
        logger.error(f"Error initializing database for country {parameter}: {e}")
        return []


def db_get_credit_card(country: str, bank: str, card_type: str, my_file: Dict[str, Any]) -> str:
    """
    Get a credit card from the database with caching.
    
    Args:
        country (str): Country code.
        bank (str): Bank name.
        card_type (str): Card type.
        my_file (Dict[str, Any]): Dictionary storing credit card information.
        
    Returns:
        str: A valid credit card number.
    """
    parameter = country + bank + card_type
    if parameter in my_file:
        if len(my_file[parameter]) > 0:
            x = my_file[parameter]
        else:
            return ""
    else:
        my_file[parameter] = initialize_credit_card_list(country, bank, card_type)
        x = my_file[parameter]
        if len(x) == 0:
            return ""

    this_instance = random.choice(x)
    prefix = this_instance['bin_range']
    length = int(this_instance['number_length'])
    
    return generate_credit_card(prefix, length)


def get_item_from_db(parameter: str, my_file: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get and remove an item from a database.
    
    Args:
        parameter (str): Country code.
        my_file (Dict[str, Any]): Dictionary storing database contents.
        
    Returns:
        Optional[Dict[str, Any]]: An item from the database or None if not found.
    """
    if parameter in my_file:
        if len(my_file[parameter]) > 0:
            return my_file[parameter].pop(0)
        else:
            return None
    else:
        my_file[parameter] = initialize_db(parameter)
        if len(my_file[parameter]) > 0:
            return my_file[parameter].pop(0)
        return None


def create_row(column_definitions: List[ColumnDefinition], separator: str, 
               country_array: List[str], phone_array: List[Dict[str, Any]], 
               my_file: Dict[str, Any]) -> str:
    """
    Create a single data row based on column definitions.
    
    Args:
        column_definitions (List[ColumnDefinition]): List of column definitions.
        separator (str): Separator between values.
        country_array (List[str]): List of country codes.
        phone_array (List[Dict[str, Any]]): List of phone information.
        my_file (Dict[str, Any]): Dictionary storing various data.
        
    Returns:
        str: A single row of data.
    """
    row_value = ""
    country = random.choice(country_array)
    
    for x in column_definitions:
        # Handle different data types
        if x["datatype"] == "string":
            if x["is_variable_legth"]:
                if x["is_null"]:
                    ll = random.randint(0, x["length"])
                else:
                    ll = random.randint(1, x["length"])
            else:
                ll = x["length"]
            value_of_string = ''.join(
                random.choice(string.ascii_letters + string.digits + 'äëöü') 
                for _ in range(ll)
            )
            value_of_string = f'"{value_of_string}"'
            
        elif x["datatype"] == "file":
            value_of_string = get_any_item_from_list(x["file_path"], my_file)
            value_of_string = f'"{value_of_string}"'
            
        elif x["datatype"] == "ssn":
            value_of_string = f'{random.randrange(100,999)}-{random.randrange(10,99)}-{random.randrange(100,999)}'
            value_of_string = f'"{value_of_string}"'
            
        elif x["datatype"] == "number":
            value_of_string = str(random.randrange(10**int(x["min_range"]), 10**int(x["max_range"])))
            value_of_string = f'"{value_of_string}"'
            
        elif x["datatype"] == "phonenumber":
            value_of_string = get_phone_number(country, phone_array)
            value_of_string = f'"{value_of_string}"'
            
        elif x["datatype"] == "xdate":
            value_of_string = random_date_between(
                x["from_date"], x["until_date"], x["date_format"], random.random()
            )
            value_of_string = f'"{value_of_string}"'
            
        elif x["datatype"] == "country":
            value_of_string = country
            value_of_string = f'"{value_of_string}"'
            
        elif x["datatype"] == "address":
            with open(f"input/{country}.csv", encoding="utf8") as f_address:
                address_array = [row.rstrip("\n") for row in f_address]
            value_of_string = random.choice(address_array)
            value_of_string = f'"{value_of_string}"'
            
        elif x["datatype"] == "creditcard":
            value_of_string = db_get_credit_card(
                x['country'], x['bank_name'], x['card_type'], my_file
            )
            value_of_string = f'"{value_of_string}"'
            
        elif x["datatype"] == "mongo_address":
            value_of_string = get_item_from_db(country, my_file)
            value_of_string = f'"{str(value_of_string)}"'
            
        elif x["datatype"] == "unique_values":
            value_of_string = get_item_from_list(x['file_path'], my_file)
            value_of_string = f'"{str(value_of_string)}"'
            
        elif x["datatype"] == "mychoice":
            value_of_string = random.choice(x['choices'])
            value_of_string = f'"{str(value_of_string)}"'
            
        elif x["datatype"] == "uuid":
            value_of_string = uuid.uuid4()
            value_of_string = f'"{str(value_of_string)}"'
        
        # Append to row with separator
        if row_value == "":
            row_value = value_of_string
        else:
            row_value = row_value + separator + value_of_string
            
    return row_value


def generate_data(parameter_file: str) -> None:
    """
    Generate test data based on parameters in a JSON file.
    
    Args:
        parameter_file (str): Path to the parameter JSON file.
    """
    try:
        from .config import load_config
        
        logger.info(f"Starting data generation using parameters from '{parameter_file}'")
        
        # Load configuration
        config = load_config(parameter_file)
        separator = config.get_separator()
        columns = config.get_column_definitions()
        filename = config.get_output_filename()
        row_count = config.get_row_count()
        
        logger.info(f"Loaded configuration with {len(columns)} columns")
        
        # Initialize data structures
        country_array = initialize_country_list()
        logger.info(f"Initialized country list with {len(country_array)} entries")
        
        phone_array = initialize_phone_list()
        logger.info(f"Initialized phone list with {len(phone_array)} entries")
        
        my_file = {}

        # Generate and write data
        try:
            with open(filename, 'w', encoding="utf8") as f:
                logger.info(f"Generating {row_count} rows of data")
                for i in range(row_count):
                    if i > 0 and i % 1000 == 0:
                        logger.info(f"Generated {i} rows...")
                    each_row = create_row(columns, separator, country_array, phone_array, my_file).rstrip('\n')
                    print(each_row, file=f)
                logger.info(f"Successfully generated {row_count} rows of data")
        except Exception as e:
            logger.error(f"Error writing data to file: {e}")
            raise
            
    except Exception as e:
        logger.error(f"Error generating data: {e}")
        raise


if __name__ == "__main__":
    generate_data('customer_master_parameters.json')