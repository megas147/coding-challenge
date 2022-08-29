from typing import Sequence
from jsonschema import validate
import json

# schema to validate organisation data
data_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["name", "config"],
        "properties": {
            "name": {"type": "string"},
            "config": {
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "has_fixed_membership_fee": {"type": "boolean"},
                            "fixed_membership_fee_amount": {"type": "number"}
                        },
                        "required": ["has_fixed_membership_fee", "fixed_membership_fee_amount"]
                    },
                    {
                        "type": "null"
                    }
                ]
            }
        }
    }
}

# schema to validate organisation structure
structure_schema = {
    "type": "object",
    "patternProperties": {
        "^.*$": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "additionalProperties": False
}


def __read_data(path: str, schema: dict) -> Sequence[dict] | dict:
    '''Read file data and validate with schema'''
    try:
        # open file
        with open(path, "r") as read_file:
            # read file to json data
            data = json.load(read_file)
            # validate data with allowed schema
            validate(data, schema=schema)
            return data
    except Exception as ex:
        # print and reraise error in case of validation error
        print(ex)
        raise ex


def read_data(path: str) -> Sequence[dict]:
    '''read data with organisation data validation schema'''
    return __read_data(path, data_schema)


def read_structure(path: str) -> dict:
    '''read data with organisation structure validation schema'''
    return __read_data(path, structure_schema)
