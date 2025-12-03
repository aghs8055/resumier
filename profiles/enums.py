from enum import Enum

from common.mixins import ChoicesMixin


class Gender(ChoicesMixin, Enum):
    MALE = 'male'
    FEMALE = 'female'


class MilitaryService(ChoicesMixin, Enum):
    COMPLETED = 'completed'
    PENDING = 'pending'
    NOT_REQUIRED = 'not_required'


class LanguageLevel(ChoicesMixin, Enum):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    NATIVE = 'native'


class MaritalStatus(ChoicesMixin, Enum):
    SINGLE = 'single'
    MARRIED = 'married'


class Platform(ChoicesMixin, Enum):
    LINKEDIN = 'linkedin'
    X = 'x'
    INSTAGRAM = 'instagram'
    FACEBOOK = 'facebook'
    YOUTUBE = 'youtube'
    TIKTOK = 'tiktok'
    OTHER = 'other'


class SkillLevel(ChoicesMixin, Enum):
    BEGINNER = 'beginner'
    INTERMEDIATE = 'intermediate'
    ADVANCED = 'advanced'
    EXPERT = 'expert'
