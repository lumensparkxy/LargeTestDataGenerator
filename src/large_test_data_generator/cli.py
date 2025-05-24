#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line interface for Large Test Data Generator.
"""
import argparse
import sys
import os
from large_test_data_generator.data_generator import generate_data


def main():
    """
    Main function for the command-line interface.
    """
    parser = argparse.ArgumentParser(
        description="Generate test data based on parameters in a JSON file."
    )
    parser.add_argument(
        "-p", "--parameters",
        help="Path to the parameter JSON file.",
        default="customer_master_parameters.json"
    )
    args = parser.parse_args()

    if not os.path.exists(args.parameters):
        print(f"Error: Parameter file '{args.parameters}' not found.", file=sys.stderr)
        sys.exit(1)

    try:
        generate_data(args.parameters)
        print(f"Data generation completed successfully.")
    except Exception as e:
        print(f"Error generating data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()