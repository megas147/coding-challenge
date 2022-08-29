#!/usr/bin/env python3
from typing import Sequence
import unittest
from OrganisationHierarchy import OrganisationHierarchy
from Input import read_structure, read_data
from jsonschema.exceptions import ValidationError
import sys


class TestCases(unittest.TestCase):
    def run_tests(self):
        # validate -4 is invalid
        self.assertRaises(ValueError, test, -4, "week", "area_b")
        # validate above max int is invalid (in python ints can be bigger then max size)
        self.assertRaises(ValueError, test, sys.maxsize + 1, "week", "area_b")
        # validate above 2000 max week rate is invalid
        self.assertRaises(ValidationError, test, 900000, "week", "area_b")
        # validate under 25 min week rate is invalid
        self.assertRaises(ValidationError, test, 20, "week", "area_b")
        # validate above 8660 max month rate is invalid
        self.assertRaises(ValidationError, test, 900000, "month", "area_b")
        # validate under 110 min month rate is invalid
        self.assertRaises(ValidationError, test, 60, "month", "area_b")
        # validate results
        # hierarchy data should be used for 45000
        assert test(25, "week", "area_a") == 45000, "should be 45000"
        # under 120 + vat% should be 144
        assert test(25, "week", "area_b") == 144, "should be 144"
        # 500 + 20%(=100) = 600
        assert test(500, "week", "area_b") == 600, "should be 600"
        # 200 / 4 = 500 + 20%(=100) = 600
        assert test(2000, "month", "area_b") == 600, "should be 600 "
        # 115 is under 120 + vat% minimum rate
        assert test(115, "month", "area_b") == 144, "should be 144"
        # read organisation structure
        structure = read_structure("organisation-structure.json")
        # read organisation data
        data = read_data("organisation-data.json")
        # print hierarchy
        hierarchy = OrganisationHierarchy(data, structure)
        hierarchy.print_hierarchy()
        print("all tests passed :)")


def test(rent_amount: int, rent_time: str, organisation_unit_name: str) -> int:
    # read organisation structure
    structure = read_structure("organisation-structure.json")
    # read organisation data
    data = read_data("organisation-data.json")
    # create hierarchy
    hierarchy = OrganisationHierarchy(data, structure)
    # find organisation unit instance by name
    unit = hierarchy.find_one(organisation_unit_name)
    # calculate membership
    membership_fee = hierarchy.calculate_membership_fee(rent_amount, rent_time, unit)
    return membership_fee


if __name__ == "__main__":
    if len(sys.argv) == 4:
        # run test with command line arguments
        print(test(int(sys.argv[1]), sys.argv[2], sys.argv[3]))
    else:
        # run tests
        TestCases().run_tests()
