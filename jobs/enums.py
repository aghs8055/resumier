from enum import Enum

from common.mixins import ChoicesMixin


class Gender(ChoicesMixin, Enum):
    MALE = 'male'
    FEMALE = 'female'
    ANY = 'any'


class JobCategory(ChoicesMixin, Enum):
    ENGINEERING = 'engineering'
    HR = 'hr'
    FINANCE = 'finance'
    MARKETING = 'marketing'
    SALES = 'sales'
    OTHER = 'other'


class MilitaryService(ChoicesMixin, Enum):
    SHOULD_HAVE = 'should_have'
    SHOULD_NOT_HAVE = 'should_not_have'
    ANY = 'any'
