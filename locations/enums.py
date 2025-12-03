from enum import Enum

from common.mixins import ChoicesMixin


class LocationType(ChoicesMixin, Enum):
    ON_SITE = 'on_site'
    REMOTE = 'remote'
    HYBRID = 'hybrid'


class LocationLevel(ChoicesMixin, Enum):
    GLOBAL = 'global'
    CONTINENT = 'continent'
    COUNTRY = 'country'
    CITY = 'city'
    DISTRICT = 'district'
    NEIGHBORHOOD = 'neighborhood'
    STREET = 'street'
    BUILDING = 'building'
    ROOM = 'room'
