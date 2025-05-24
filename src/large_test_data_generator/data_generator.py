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

# Type aliases for better readability
ColumnDefinition = Dict[str, Any]
ParameterData = Dict[str, Any]


def initialize_country_list() -> List[str]:
    """
    Initialize country list from MongoDB with weights.
    
    Returns:
        List[str]: A list of country codes, with frequency based on weights.
    """
    uri = f'mongodb://{os.environ.get("MONGOUSER")}:{os.environ.get("MONGOPASSWORD")}@{os.environ.get("MONGOSERVER")}:27017'
    country_client = pymongo.MongoClient(uri)
    country_db = country_client.iso
    country_coll = country_db.details
    country_cursor = country_coll.find({'for_address': 1})

    country_list = []
    for a in country_cursor:
        temp = [a['alpha-2']] * int(a['weight'])
        country_list.extend(temp)
    return country_list


def initialize_phone_list() -> List[Dict[str, Any]]:
    """
    Initialize phone number list from MongoDB.
    
    Returns:
        List[Dict[str, Any]]: A list of phone number information.
    """
    uri = f'mongodb://{os.environ.get("MONGOUSER")}:{os.environ.get("MONGOPASSWORD")}@{os.environ.get("MONGOSERVER")}:27017'
    phone_client = pymongo.MongoClient(uri)
    phone_db = phone_client.iso
    phone_coll = phone_db.details
    phone_cursor = phone_coll.find({}, {'_id': 0, 'alpha-2': 1, 'dialCode': 1, 'eg_phone_number': 1})
    
    phone_list = []
    for phone_number in phone_cursor:
        phone_list.append(phone_number)
    
    return phone_list


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
    
    return time.strftime(date_format, time.localtime(ptime))


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


def get_credit_card(country: str, bank_name: str, card_type: str) -> str:
    """
    Generate a valid credit card number for the specified country, bank, and card type.
    
    Args:
        country (str): Country code.
        bank_name (str): Bank name.
        card_type (str): Card type (e.g., "mastercard", "visa").
        
    Returns:
        str: A valid credit card number.
    """
    uri = f'mongodb://{os.environ.get("MONGOUSER")}:{os.environ.get("MONGOPASSWORD")}@{os.environ.get("MONGOSERVER")}:27017'
    client = pymongo.MongoClient(uri)
    db = client.creditcards
    cursor = db.details
    
    x = cursor.find({'country': country, 'bank_name': bank_name, 'card_type': card_type})
    count = x.count()
    if count == 0:
        return ""
        
    this_instance = x[random.randint(0, count-1)]
    prefix = this_instance['bin_range']
    
    length = int(this_instance['number_length'])
    credit_card = prefix
    for i in range(1, length-len(prefix)):
        credit_card += str(random.choice(range(0, 10)))
    
    # Find a valid check digit
    for i in range(0, 10):
        candidate = credit_card + str(i)
        if is_valid_card(candidate):
            credit_card = candidate
            break
    
    return credit_card


def get_address(country: str) -> Optional[Dict[str, Any]]:
    """
    Get a random address from MongoDB for the specified country.
    
    Args:
        country (str): Country code.
        
    Returns:
        Optional[Dict[str, Any]]: A random address or None if not found.
    """
    uri = f'mongodb://{os.environ.get("MONGOUSER")}:{os.environ.get("MONGOPASSWORD")}@{os.environ.get("MONGOSERVER")}:27017'
    address_client = pymongo.MongoClient(uri)
    address_db = address_client.postal_address
    address_cursor = address_db.details
    
    x = address_cursor.aggregate([
        {'$sample': {'size': 1}},
        {'$match': {'country': country}},
        {'$out': 'random_address'}
    ])
    address_client.close()
    
    address_client = pymongo.MongoClient(uri)
    address_db = address_client.postal_address
    address_cursor = address_db.random_address
    
    if address_cursor.count() == 0:
        return None
    else:
        single_one = address_cursor.find({}, {'_id': 0})
        return single_one[0]


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


def initialize_db(parameter: str) -> List[Dict[str, Any]]:
    """
    Initialize database with addresses for a specific country.
    
    Args:
        parameter (str): Country code.
        
    Returns:
        List[Dict[str, Any]]: List of addresses.
    """
    uri = f'mongodb://{os.environ.get("MONGOUSER")}:{os.environ.get("MONGOPASSWORD")}@{os.environ.get("MONGOSERVER")}:27017'
    address_client = pymongo.MongoClient(uri)
    address_db = address_client.postal_address
    address_cursor = address_db.details
    
    x = address_cursor.aggregate([
        {'$sample': {'size': 10000}},
        {'$match': {'country': parameter}},
        {'$out': 'random_address'}
    ])
    address_client.close()
    
    address_client = pymongo.MongoClient(uri)
    address_db = address_client.postal_address
    address_cursor = address_db.random_address
    
    addresses = address_cursor.find({}, {'_id': 0})
    
    temp_list = []
    for each_address in addresses:
        temp_list.append(each_address)
    
    return temp_list


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
    uri = f'mongodb://{os.environ.get("MONGOUSER")}:{os.environ.get("MONGOPASSWORD")}@{os.environ.get("MONGOSERVER")}:27017'
    cc_client = pymongo.MongoClient(uri)
    cc_db = cc_client.creditcards
    cc_cursor = cc_db.details
    
    cc = cc_cursor.find(
        {'country': country, 'bank_name': bank, 'card_type': card_type},
        {'_id': 0}
    )
    
    temp_list = []
    for each_cc in cc:
        temp_list.append(each_cc)
    
    return temp_list


def db_get_credit_card(country: str, bank: str, card_type: str, my_file: Dict[str, Any]) -> str:
    """
    Get a credit card from the database.
    
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
    credit_card = prefix
    for i in range(1, length-len(prefix)):
        credit_card += str(random.choice(range(0, 10)))
    
    # Find a valid check digit
    for i in range(0, 10):
        pp = credit_card + str(i)
        if is_valid_card(pp):
            credit_card = pp
            break
    
    return credit_card


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
    # Initialize data structures
    country_array = initialize_country_list()
    phone_array = initialize_phone_list()
    my_file = {}

    # Read parameter file
    with open(parameter_file) as data_file:
        data = json.load(data_file)
    separator = data["separator"]

    # Generate and write data
    with open(data["filename"], 'w', encoding="utf8") as f:
        for i in range(data["number_of_rows"]):
            each_row = create_row(data["columns"], separator, country_array, phone_array, my_file).rstrip('\n')
            print(each_row, file=f)


if __name__ == "__main__":
    generate_data('customer_master_parameters.json')