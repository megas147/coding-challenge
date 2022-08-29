import sys
from typing import Sequence
from jsonschema.exceptions import ValidationError
from anytree import NodeMixin, RenderTree, find
from settings import MAX_MONTH_RENT, MAX_WEEK_RENT, \
                     MIN_MEMBERSHIP_RENT, MIN_MONTH_RENT, MIN_WEEK_RENT, VAT


def add_percentage(value: int, percentage: int) -> int:
    '''takes in a value and how much percentage to add to given value'''
    return value + (value * (percentage / 100))


class OrganisationUnit(NodeMixin):
    def __init__(self, name, config=None, parent=None, children=None) -> None:
        super(OrganisationUnit, self).__init__()
        self.name = name
        self.config = config
        self.parent = parent
        if children:
            self.children = children

    def __repr__(self):
        return self.name


class OrganisationHierarchy:
    def __init__(self, data: Sequence[dict], structure: dict):
        # preparation of tree creation
        # map organisation data to name -> config for faster search
        config_map = {
            value["name"]: value["config"] for value in data
        }

        # first thing find the root node
        # create a flattened list of child nodes for easy search
        children = [item for sublist in structure for item in sublist]
        # find parent node by searching if node name is in children structures
        for key in structure.keys():
            # no children whith this key, means its the root node
            if key not in children:
                self.root = OrganisationUnit(key, config_map[key])
                break  # root node is complete, exit early

        # handle children recursively
        self.__create(self.root, structure, config_map)


    def print_hierarchy(self) -> None:
        '''prints organisation tree'''
        print(RenderTree(self.root))


    def find_one(self, name: str) -> OrganisationUnit:
        '''find organisation unit by name'''
        return find(self.root, lambda n: name == n.name)


    def get_fixed_membership_fee(self, organisation_unit: OrganisationUnit) -> int | None:
        '''get fixed membership fee from organisation hierarchy'''
        # if current organisation unit has config and fixed membership fee
        if organisation_unit.config and organisation_unit.config["has_fixed_membership_fee"]:
            return organisation_unit.config["fixed_membership_fee_amount"]
        elif organisation_unit.parent:
            # recursive run while parent node exists
            return self.get_fixed_membership_fee(organisation_unit.parent)
        else:
            return None


    def calculate_membership_fee(self, rent_amount: int, rent_period: str, organisation_unit: OrganisationUnit) -> int:
        '''Calculate membership fee based on rent amount, rent period and organisation unit'''
        # get membership fees
        membership_fee = self.get_fixed_membership_fee(organisation_unit)
        # if organisation hierarchy has a membership fee, return it
        if membership_fee is not None:
            return int(membership_fee)

        # if no membership fee in hierarchy data
        # validate input is > 1 and < sys.maxsize
        if rent_amount < 1 or rent_amount > sys.maxsize:
            raise ValueError(f"Invalid rent_amount {rent_amount} must be between 1 and {sys.maxsize}.")

        if rent_period not in ["month", "week"]:
            raise ValueError(f"Invalid rent_period {rent_period} must be 'month' or 'week'.")

        # rule validation
        if rent_period == "week" and rent_amount < MIN_WEEK_RENT:
            raise ValidationError(f"Minimum rent amount is £{MIN_WEEK_RENT} per week")

        if rent_period == "week" and rent_amount > MAX_WEEK_RENT:
            raise ValidationError(f"Maximum rent amount is £{MAX_WEEK_RENT} per week")

        if rent_period == "month" and rent_amount < MIN_MONTH_RENT:
            raise ValidationError(f"Minimum rent amount is £{MIN_MONTH_RENT} per month")

        if rent_period == "month" and rent_amount > MAX_MONTH_RENT:
            raise ValidationError(f"Maximum rent amount is £{MAX_MONTH_RENT} per month")

        # if rent period is in months, calculate rent for 1 week
        if rent_period == "month":
            # assuming 1 month equals 4 weeks
            rent_amount = rent_amount / 4

        membership_fee = add_percentage(rent_amount, VAT)
        # Minimum membership fee is £120 + VAT - if the rent is lower than £120
        # the membership fee stays at £120 + VAT

        minimum_membership_fee = add_percentage(MIN_MEMBERSHIP_RENT, VAT)

        if membership_fee < minimum_membership_fee:
            membership_fee = minimum_membership_fee

        return int(membership_fee)


    def __create(self, parent, structure, config_map):
        '''private method to recursively create all child nodes'''
        for key, values in structure.items():
            if key == parent.name:
                for value in values:
                    node = OrganisationUnit(value, config_map[value], parent=parent)
                    self.__create(node, structure, config_map)
