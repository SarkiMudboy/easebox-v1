from typing import Any, List, Optional, Dict, Tuple
from unittest.mock import Base
from pydantic import (
    BaseModel, ValidationError, 
    Field, SecretStr, 
    EmailStr, field_validator,
    StrictBool, ConfigDict,
    ValidationInfo, model_validator
    )
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import AbstractBaseUser
from ..enums import OperatingCities, OperatingStates

from .validators import PhoneNumber

User: AbstractBaseUser = get_user_model()


class BaseUser(BaseModel):

    model_config = ConfigDict(arbitrary_types_allowed=True)

    first_name: str
    last_name :str
    email: str
    phone_number: str


class BasePhone(BaseModel):

    phone_number: PhoneNumber

class BaseEmail(BaseModel):

    email: EmailStr = Field(max_length=300)


class BasePassword(BaseModel):

    password: str       

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str, values: ValidationInfo) -> str:

        try:
            password_validation.validate_password(password)

        except Exception as e:
            raise ValueError(str(e))
        
        return password

class BaseEaseboxUser(BaseUser, BaseEmail, BasePhone, BasePassword):

    user: AbstractBaseUser


class Verified(BasePhone, BaseEmail):

    phone_number: Optional[PhoneNumber] = None
    email: Optional[EmailStr] = None

    @model_validator(mode="after")
    def check_identifiers(self) -> 'Verified':

        if not self.phone_number and not self.email:
            raise ValueError("Please provide an email or phone")
        
        return self

    @field_validator("email", "phone_number")
    @classmethod
    def validate(cls, ID: str, values: ValidationInfo) -> str:

        query = {f"{values.field_name}__iexact": ID}
        
        user = User.objects.get(**query)
        
        if values.field_name == "email" and user.is_email_verified:
            raise ValueError("This email has already been verified")
        
        if values.field_name == "phone_number" and user.is_phone_number_verified:
            raise ValueError("This phone number has already been verified")
        
        return ID


class BaseBusiness(BaseModel):

    name: str = Field(max_length=600)
    address: str = Field(max_lenth=600)
    city: str = Field(max_lenth=600)
    state: str = Field(max_lenth=100)
    category: Optional[str] = None

    @model_validator(mode="after")
    def validate_locations_type(self) -> 'BaseBusiness':
        
        assert self.city.isalpha(), "Name must contain only alphabets"
        assert self.state.isalpha(), "Name must contain only alphabets"

        return self

    @model_validator(mode="after")
    def check_supported_locations(self) -> 'BaseBusiness':

        if self.city.upper() not in OperatingCities.items:
            raise ValueError(f"{self.city} not supported")

        if self.state.upper() not in OperatingStates.items:
            raise ValueError(f"{self.state} not supported")
        
        return self

    @field_validator("city", "state")
    @classmethod
    def validate_location(cls, v: str, value: ValidationInfo) -> str:
        assert v.isalpha(), f"{value.field_name} must contain only alphabets"
        return v

class Business(BaseEaseboxUser, BaseBusiness):

    ...

    
class BusinessUser(BaseUser, BaseEmail, BasePhone, BasePassword):
    # User

    model_config= ConfigDict(arbitrary_types_allowed=True)

    first_name: str = Field(max_length=250)
    last_name :str = Field(max_length=250)

    email: Optional[EmailStr] = None
    phone_number: Optional[PhoneNumber] = None
    
    password: str = Field(max_length=250)
    accept_terms_and_privacy: StrictBool = Field(default=False)

    # Business
    business: Optional[BaseBusiness] = None

    @field_validator("email", "phone_number")
    @classmethod
    def validate_identifiers(cls, identifier: str, value: ValidationInfo) -> str:
    
        query = {f"{value.field_name}__iexact": identifier}

        if User.objects.filter(**query).exists():
            raise ValueError(f"User with this {value.field_name} already exists")
        
        return identifier

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_names(cls, name: str, value: ValidationInfo) -> str:
        assert name.isalpha(), f"{value.field_name} is not a valid name"
        return name
    
    @field_validator("accept_terms_and_privacy")
    @classmethod
    def validate_accept_terms(cls, v: bool) -> bool:

        assert v == True, "You must accept terms and privacy to continue"
        return v
