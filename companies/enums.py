from enum import Enum

from common.mixins import ChoicesMixin


class Perk(ChoicesMixin, Enum):
    HEALTH_INSURANCE = 'health_insurance'
    DENTAL_INSURANCE = 'dental_insurance'
    VISION_INSURANCE = 'vision_insurance'
    RETIREMENT_PLAN = 'retirement_plan'
    PARENTAL_LEAVE = 'parental_leave'


class CompanySize(ChoicesMixin, Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    ENTREPRISE = 'entreprise'
    OTHER = 'other'