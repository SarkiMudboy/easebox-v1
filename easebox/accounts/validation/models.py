from typing import Any, List, Optional, Dict, Tuple
from pydantic import BaseModel, ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser

User: AbstractBaseUser = get_user_model()

# Validation here will be where I will customize the error messages
# Base model classes  of every model then inherited in concrete classes where actual validation function will be written 

class User(BaseModel):

    first_name: str
    lastname: str
    email: str
    phone_number: str
    password: str

class Business(BaseModel):

    name: str
    address: str
    category: str

class Phone(BaseModel): ...