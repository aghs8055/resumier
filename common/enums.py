from enum import Enum

from common.mixins import ChoicesMixin


class EducationLevel(ChoicesMixin, Enum):
    HIGH_SCHOOL = 'high_school'
    BACHELOR = 'bachelor'
    MASTER = 'master'
    DOCTORATE = 'doctorate'
    OTHER = 'other'


class ContractType(ChoicesMixin, Enum):
    FULL_TIME = 'full_time'
    PART_TIME = 'part_time'
    CONTRACT = 'contract'
    VOLUNTEER = 'volunteer'
    OTHER = 'other'


class Currency(ChoicesMixin, Enum):
    USD = 'usd'
    EUR = 'eur'
    IRR = 'irr'
    OTHER = 'other'


class Language(ChoicesMixin, Enum):
    PERSIAN = 'fa'
    ENGLISH = 'en'


class ProcessStatus(ChoicesMixin, Enum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    FINISHED = 'FINISHED'
    FAILED = 'FAILED'


class ExperienceLevel(ChoicesMixin, Enum):
    ENTRY = 'entry'
    MID = 'mid'
    SENIOR = 'senior'
    PRINCIPAL = 'principal'
    OTHER = 'other'