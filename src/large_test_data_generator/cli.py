#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line interface for Large Test Data Generator.
"""
import argparse
import sys
import os
from large_test_data_generator.data_generator import generate_data
from large_test_data_generator.logger import logger


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
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose logging",
        action="store_true"
    )
    args = parser.parse_args()

    # Set logging level based on verbosity
    if args.verbose:
        import logging
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    if not os.path.exists(args.parameters):
        logger.error(f"Error: Parameter file '{args.parameters}' not found.")
        sys.exit(1)

    try:
        generate_data(args.parameters)
        logger.info("Data generation completed successfully.")
    except Exception as e:
        logger.error(f"Error generating data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()