# Large Test Data Generator

Generate CSV files for large data requirements based on customizable parameters.

## Overview

This tool allows you to generate test data in CSV format according to specifications defined in a JSON parameter file. It supports a variety of data types and can generate millions of records efficiently.

## Installation

```bash
# Install from source
pip install -e .
```

## Usage

### Command Line

```bash
# Generate data using default parameters file (customer_master_parameters.json)
generate-test-data

# Generate data using a custom parameters file
generate-test-data --parameters custom_parameters.json
```

### As a Python Module

```python
from large_test_data_generator.data_generator import generate_data

# Generate data using a parameters file
generate_data('customer_master_parameters.json')
```

## Parameter File Format

The parameter file is a JSON file that controls everything. It contains all the required definitions as key-value pairs:

| Key | Description |
|-----|-------------|
| `filename` | Name of the CSV file to be created |
| `columns` | Definition of columns to be created in the CSV file |
| `columns.column_name` | Column name |
| `columns.datatype` | Data type of column. It can be **string** or **reference to another column** or **values in file** |
| `columns.length` | Length of the column |
| `columns.is_variable_length` | If the length can vary or is fixed length. Values: `true` or `false` |
| `columns.is_null` | Is null allowed. If `true` then length can be 0 |
| `columns.file_path` | If the datatype is `file`, it looks for the values from the file at this path |
| `separator` | Separator between the columns |
| `number_of_rows` | Number of rows to be produced in the file |

### Supported Data Types

- `string`: Random string with specified length
- `file`: Values from a file
- `ssn`: Social Security Number format
- `number`: Random number in a range
- `phonenumber`: Random phone number for a country
- `xdate`: Random date between two dates
- `country`: Country code
- `address`: Address from a file
- `creditcard`: Valid credit card number
- `mongo_address`: Address from MongoDB
- `unique_values`: Unique values from a file
- `mychoice`: Random choice from a list
- `uuid`: UUID value

## Example Parameter File

```json
{
  "filename": "output.csv",
  "columns": [
    {
      "column_name": "id",
      "datatype": "uuid"
    },
    {
      "column_name": "full_name",
      "datatype": "string",
      "length": 30,
      "is_null": false,
      "is_variable_length": true
    },
    {
      "column_name": "birthdate",
      "datatype": "xdate",
      "from_date": "01.JAN.1950 00:00:00",
      "until_date": "31.DEC.2000 23:59:59",
      "date_format": "%d.%b.%Y"
    }
  ],
  "number_of_rows": 1000,
  "separator": ","
}
```

## MongoDB Integration

The tool can connect to MongoDB to retrieve and generate data. Set the following environment variables:

- `MONGOUSER`: MongoDB username
- `MONGOPASSWORD`: MongoDB password
- `MONGOSERVER`: MongoDB server address

## License

Released under the [MIT License](LICENSE).
