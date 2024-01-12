from typing import Any, List, Optional, Dict, Tuple
from pydantic import (
    BaseModel, ValidationError, 
    Field, SecretStr, 
    EmailStr, field_validator,
    StrictBool, ConfigDict,
    ValidationInfo
    )
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.models import AbstractBaseUser

User: AbstractBaseUser = get_user_model()

# Validation here will be where I will customize the error messages
# Base model classes  of every model then inherited in concrete classes where actual validation function will be written 

class BaseUser(BaseModel):

    model_config_dict = ConfigDict(arbitrary_types_allowed=True)

    first_name: str
    lastname :str
    email: str
    phone_number: str


class BasePhone(BaseModel):

    phone_number: str


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
            
            errors = list(e)
            raise ValueError(errors[0])
        
        return password

class BaseEaseboxUser(BaseUser, BaseEmail, BasePhone, BasePassword):

    user: AbstractBaseUser

class BaseBusiness(BaseModel):

    name: str
    address: str
    city: str
    state: str
    category: str
    rc_num: Optional[str]

    # some validations for city and state -> ensure its not new values. I am not sure these guys (models) dis-allow it

class Business(BaseEaseboxUser, BaseBusiness):

    # Business
    business_name: str = Field(max_length=600, serialization_alias="name", validation_alias="name")
    address: str = Field(max_lenth=600, required=True)
    city: str = Field(max_lenth=600)
    state: str = Field(max_lenth=100)
    category: Optional[str]

    
class BusinessUser(BaseUser, BaseEmail, BasePhone, BasePassword, BaseBusiness):
    # User

    first_name: str = Field(max_length=250, required=True)
    lastname :str = Field(max_length=250, required=True)

    email: Optional[EmailStr] = Field(description="User's email address")
    phone_number: Optional[str] = Field(description="User's phone number")
    
    password: SecretStr = Field(max_length=250)
    accept_terms_and_privacy: StrictBool = Field(default=False)

    # Business
    business_name: str = Field(max_length=600, serialization_alias="name", validation_alias="name")
    address: str = Field(max_lenth=600, required=True)
    city: str = Field(max_lenth=600)
    state: str = Field(max_lenth=100)
    category: Optional[str]