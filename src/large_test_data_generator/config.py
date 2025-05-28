#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration handling for Large Test Data Generator.
"""
import json
import os
from typing import Dict, Any, Optional
from .logger import logger


class Config:
    """Configuration manager for the data generator."""

    def __init__(self, config_file: str = None):
        """
        Initialize the configuration.
        
        Args:
            config_file (str, optional): Path to the configuration file.
        """
        self.config_file = config_file or 'customer_master_parameters.json'
        self.config = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from the specified file."""
        try:
            with open(self.config_file, 'r', encoding='utf8') as f:
                self.config = json.load(f)
            logger.info(f"Loaded configuration from {self.config_file}")
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_file} not found")
            raise
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file {self.config_file}")
            raise
        
        # Validate required fields
        required_fields = ['filename', 'columns', 'separator', 'number_of_rows']
        for field in required_fields:
            if field not in self.config:
                logger.error(f"Required field '{field}' missing from configuration")
                raise ValueError(f"Required field '{field}' missing from configuration")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key (str): Configuration key.
            default (Any, optional): Default value if key not found.
            
        Returns:
            Any: Configuration value.
        """
        return self.config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """
        Get a configuration value using dictionary syntax.
        
        Args:
            key (str): Configuration key.
            
        Returns:
            Any: Configuration value.
            
        Raises:
            KeyError: If key not found.
        """
        return self.config[key]
    
    def get_output_filename(self) -> str:
        """
        Get the output filename from configuration.
        
        Returns:
            str: Output filename.
        """
        return self.config.get('filename', 'output.csv')
    
    def get_column_definitions(self) -> list:
        """
        Get column definitions from configuration.
        
        Returns:
            list: Column definitions.
        """
        return self.config.get('columns', [])
    
    def get_separator(self) -> str:
        """
        Get the separator from configuration.
        
        Returns:
            str: Separator character.
        """
        return self.config.get('separator', ',')
    
    def get_row_count(self) -> int:
        """
        Get the number of rows to generate from configuration.
        
        Returns:
            int: Number of rows.
        """
        return self.config.get('number_of_rows', 100)


def load_config(config_file: str = None) -> Config:
    """
    Load configuration from a file.
    
    Args:
        config_file (str, optional): Path to the configuration file.
        
    Returns:
        Config: Configuration object.
    """
    return Config(config_file)