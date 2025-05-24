#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logging configuration for Large Test Data Generator.
"""
import logging
import os
import sys


def setup_logger(name: str = "large_test_data_generator") -> logging.Logger:
    """
    Set up a logger with the specified name.
    
    Args:
        name (str): Logger name.
        
    Returns:
        logging.Logger: Configured logger.
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Create file handler if log directory exists
    log_dir = os.path.join(os.getcwd(), "logs")
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception:
            pass
    
    if os.path.exists(log_dir):
        file_handler = logging.FileHandler(os.path.join(log_dir, f"{name}.log"))
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


# Create a default logger
logger = setup_logger()