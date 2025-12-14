from enum import Enum

from common.mixins import ChoicesMixin


class CompanySize(ChoicesMixin, Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    ENTREPRISE = 'entreprise'
    OTHER = 'other'