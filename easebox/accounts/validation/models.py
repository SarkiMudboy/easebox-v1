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

    phone: PhoneNumber
    email: EmailStr

    @field_validator("email", "phone")
    @classmethod
    def validate(cls, ID: str, values: ValidationInfo) -> str:

        query = {f"{values.field_name}__iexact": ID}
        
        user = User.objects.get(**query)

        if ID == "email" and user.is_email_verified:
            raise ValueError("This email has already been verified")
        
        if ID == "phone number" and user.is_phone_number_verified:
            raise ValueError("This phone number has already been verified")
        
        return ID


class BaseBusiness(BaseModel):

    name: str
    address: str
    city: str
    state: str
    category: str
    rc_num: Optional[str] = None

    @model_validator(mode="after")
    def validate_locations_type(self) -> 'BaseBusiness':
        
        assert self.city.isalpha(), "Name must contain only alphabets"
        assert self.state.isalpha(), "Name must contain only alphabets"

        return self

    @model_validator(mode="after")
    def check_supported_locations(self) -> 'BaseBusiness':

        if self.city not in OperatingCities.choices: 
            raise ValueError(f"{self.city} not supported")

        if self.state not in OperatingStates.choices:
            raise ValueError(f"{self.state} not supported")
        
        return self

    @field_validator("city", "state")
    @classmethod
    def validate_location(cls, v: str, value: ValidationInfo) -> str:
        assert v.isalpha(), f"{value.field_name} must contain only alphabets"
        return v

class Business(BaseEaseboxUser, BaseBusiness):

    # Business
    name: str = Field(max_length=600)
    address: str = Field(max_lenth=600, required=True)
    city: str = Field(max_lenth=600, required=True)
    state: str = Field(max_lenth=100, required=True)
    category: Optional[str]

    
class BusinessUser(BaseUser, BaseEmail, BasePhone, BasePassword, BaseBusiness):
    # User

    first_name: str = Field(max_length=250, required=True)
    last_name :str = Field(max_length=250, required=True)

    email: Optional[EmailStr] = Field(description="User's email address")
    phone_number: Optional[PhoneNumber] = Field(description="User's phone number")
    
    password: str = Field(max_length=250)
    accept_terms_and_privacy: StrictBool = Field(default=False)

    # Business
    name: str = Field(max_length=600, required=True)
    address: str = Field(max_lenth=600, required=True)
    city: str = Field(max_lenth=600, required=True)
    state: str = Field(max_lenth=100, required=True)
    category: Optional[str] = None

    # phone num in its base


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
