#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to convert the Jupyter notebook to a Python script.
"""
import nbformat
from nbconvert import PythonExporter


def convert_notebook_to_script(notebook_path, output_path):
    """
    Convert a Jupyter notebook to a Python script.
    
    Args:
        notebook_path (str): Path to the Jupyter notebook.
        output_path (str): Path to save the Python script.
    """
    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    
    # Configure the exporter
    python_exporter = PythonExporter()
    
    # Convert the notebook to Python
    python_code, _ = python_exporter.from_notebook_node(notebook)
    
    # Save the Python code to a file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(python_code)
    
    print(f"Converted {notebook_path} to {output_path}")


if __name__ == "__main__":
    convert_notebook_to_script(
        "create_test_data.ipynb",
        "create_test_data.py"
    )