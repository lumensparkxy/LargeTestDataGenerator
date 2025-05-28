#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB utility functions for Large Test Data Generator.
"""
from typing import Dict, List, Any, Optional, Union
import os
import pymongo


def get_mongodb_uri() -> str:
    """
    Get the MongoDB URI from environment variables.
    
    Returns:
        str: MongoDB URI.
    """
    mongo_user = os.environ.get("MONGOUSER", "")
    mongo_password = os.environ.get("MONGOPASSWORD", "")
    mongo_server = os.environ.get("MONGOSERVER", "localhost")
    
    return f'mongodb://{mongo_user}:{mongo_password}@{mongo_server}:27017'


def get_country_list() -> List[str]:
    """
    Get a list of countries from MongoDB with their weights.
    
    Returns:
        List[str]: List of country codes, with frequency based on weights.
    """
    uri = get_mongodb_uri()
    client = pymongo.MongoClient(uri)
    db = client.iso
    collection = db.details
    cursor = collection.find({'for_address': 1})
    
    country_list = []
    for country in cursor:
        temp = [country['alpha-2']] * int(country['weight'])
        country_list.extend(temp)
    
    client.close()
    return country_list


def get_phone_list() -> List[Dict[str, Any]]:
    """
    Get a list of phone number information from MongoDB.
    
    Returns:
        List[Dict[str, Any]]: List of phone number information.
    """
    uri = get_mongodb_uri()
    client = pymongo.MongoClient(uri)
    db = client.iso
    collection = db.details
    cursor = collection.find({}, {'_id': 0, 'alpha-2': 1, 'dialCode': 1, 'eg_phone_number': 1})
    
    phone_list = []
    for phone in cursor:
        phone_list.append(phone)
    
    client.close()
    return phone_list


def get_address_from_db(country: str) -> Optional[Dict[str, Any]]:
    """
    Get a random address from MongoDB for a specific country.
    
    Args:
        country (str): Country code.
        
    Returns:
        Optional[Dict[str, Any]]: A random address or None if not found.
    """
    uri = get_mongodb_uri()
    client = pymongo.MongoClient(uri)
    db = client.postal_address
    collection = db.details
    
    # Aggregate to get a random sample
    collection.aggregate([
        {'$sample': {'size': 1}},
        {'$match': {'country': country}},
        {'$out': 'random_address'}
    ])
    
    # Check if we got a result
    random_address = db.random_address
    if random_address.count() == 0:
        client.close()
        return None
    
    # Get the address
    address = random_address.find_one({}, {'_id': 0})
    client.close()
    return address


def get_credit_card_info(country: str, bank: str, card_type: str) -> List[Dict[str, Any]]:
    """
    Get credit card information from MongoDB.
    
    Args:
        country (str): Country code.
        bank (str): Bank name.
        card_type (str): Card type.
        
    Returns:
        List[Dict[str, Any]]: List of credit card information.
    """
    uri = get_mongodb_uri()
    client = pymongo.MongoClient(uri)
    db = client.creditcards
    collection = db.details
    
    cursor = collection.find(
        {'country': country, 'bank_name': bank, 'card_type': card_type},
        {'_id': 0}
    )
    
    result = list(cursor)
    client.close()
    return result