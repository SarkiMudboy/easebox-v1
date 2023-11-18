from enum import Enum, IntEnum
  
# create an ABC for enums to inherit (put in abstract)


class AccountStatus(str, Enum):
    ACTIVE = "AC"
    PENDING = "PN"
    SUSPENDED = "SUS"

    @classmethod
    def choices(cls) -> list:
        return [(key.value, key.name) for key in cls]


class Rating(IntEnum):

    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    @classmethod
    def choices(cls) -> list:
        return [(key.value, key.name) for key in cls]
    

class Visibility(str, Enum):

    ONLINE = "ON"
    OFFLINE = "OFF"

    @classmethod
    def choices(cls) -> list:
        return [(key.value, key.name) for key in cls]
    
# should remove but so as not to break something idk..
class PricingFactor(Enum):
    
    WEIGHT = ("WGHT")
    DISTANCE = ("DIST")
    @classmethod
    def choices(cls) -> list:
        return [(key.value, key.name) for key in cls]

class VehicleType(str, Enum):
    
    MOTORCYCLE = "MC"
    BICYCLE = "BC"
    CAR = "CR"
    VAN = "VN"

    @classmethod
    def choices(cls) -> list:
        return [(key.value, key.name) for key in cls]
    
class Plans(str, Enum):

    FREE = "FREE"
    BASIC = "BASIC"

    @classmethod
    def choices(cls) -> list:
        return [(key.value, key.name) for key in cls]


class UserVerificationIDType(str, Enum):

    NIN = "NIN"
    VOTER_CARD = "VC"
    DRIVER_LISCENCE = "DL"
    
    @classmethod
    def choices(cls) -> list:
        return [(key.value, key.name) for key in cls]



    

