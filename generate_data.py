#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script to run the Large Test Data Generator.
"""
from src.large_test_data_generator.data_generator import generate_data
import sys
import os


def main():
    """
    Main function to run the data generator.
    """
    # Check if a parameter file is provided
    if len(sys.argv) > 1:
        parameter_file = sys.argv[1]
        if not os.path.exists(parameter_file):
            print(f"Error: Parameter file '{parameter_file}' not found.")
            sys.exit(1)
    else:
        parameter_file = 'customer_master_parameters.json'
        if not os.path.exists(parameter_file):
            print(f"Error: Default parameter file '{parameter_file}' not found.")
            sys.exit(1)
    
    # Generate data
    print(f"Generating data using parameters from '{parameter_file}'...")
    generate_data(parameter_file)
    print("Data generation completed successfully.")


if __name__ == "__main__":
    main()