from pyexpat import model
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

import uuid
import pyotp

from .managers import UserManager
from .enums import (AccountStatus, Rating, Visibility, 
                   Plans, VehicleType, UserVerificationIDType,
                )


User = settings.AUTH_USER_MODEL

class TimestampMixin(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

class VerificationMixin(models.Model):

    id_type = models.CharField(choices=UserVerificationIDType.choices(), default=UserVerificationIDType.NIN)
    id_verified = models.BooleanField(default=False)
    id_num = models.URLField(_("Document"), default="")

    class Meta:
        abstract = True


class User(AbstractBaseUser, PermissionsMixin, TimestampMixin):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(_("email_address"), unique=True, null=True, blank=True)
    phone_number = models.CharField(_("Phone number"), unique=True, null=True, blank=True)

    first_name = models.CharField(verbose_name="first name", max_length=250)
    last_name = models.CharField(verbose_name="last name", max_length=250)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    failed_login_attempts = models.IntegerField(default=0)

    address = models.CharField(_("Address"), null=True, blank=True)
    image = models.URLField(_("Profile picture url"), default="")
    saved = models.ForeignKey("Saved", null=True, blank=True, on_delete=models.CASCADE)
    is_email_verified = models.BooleanField(default=False)
    is_phone_number_verified = models.BooleanField(default=False)
    accept_terms = models.BooleanField(default=False)

    phone_number_verification_key = models.CharField(max_length=100, unique=True, null=True, blank=True)
    email_verification_key = models.CharField(max_length=100, unique=True, null=True, blank=True)
    
    email_verification_key_expires = models.DateTimeField(_("Email key expires at"), null=True)

    # support_tickets = models.Model(Tickets, null=True, blank=True, on_delete=models.CASCADE())

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self) -> str:

        if self.email:
            return self.email
        
        return self.phone_number
    
    def has_perm(self, perm, obj=None) -> bool:
        return True
    
    def has_module_perms(self, app_label) -> bool:
        return True


class UserAccount(TimestampMixin, models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    owner = models.OneToOneField(User, related_name="account", on_delete=models.CASCADE)
    plan = models.CharField(choices=Plans.choices(), default=Plans.FREE)
    status = models.CharField(_("Account status"), choices=AccountStatus.choices(), default=AccountStatus.PENDING)

    def __str__(self) -> str:

        return "oooo"

class Business(TimestampMixin, models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(User, related_name="business", on_delete=models.CASCADE)
    name = models.CharField(_("Business name"), max_length=600)
    # description = models.TextField(max_length=1000, null=True, blank=True)
    address = models.CharField(_("Business address"), null=True, blank=True) # may need to split this into street, city etc.
    
    # image = models.URLField(_("Business logo url"), default="")
    rc_num = models.CharField(_("RC Number"), null=True, blank=True)
    category = models.CharField(_("Category"), max_length=300, null=True, blank=True)
    # products = models.ManyToManyField("Products", related_name="business")
    # deliveries = models.ManyToManyField(Delivery, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name


class Rider(TimestampMixin, VerificationMixin, models.Model):

    vehicle = models.ForeignKey("Vehicle", null=True, blank=True, on_delete=models.CASCADE)
    is_available = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)
    reviews = models.ManyToManyField("Review")
    rating = models.IntegerField(_("Rating"), choices=Rating.choices(), null=True, blank=True)
    # deliveries = models.ManyToManyField(Delivery, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.owner.first_name + " " + self.owner.last_name
    

class IndividualRider(Rider):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.OneToOneField(User, related_name="individual", on_delete=models.CASCADE)
    
class CompanyRider(Rider):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.OneToOneField(User, related_name="employed", on_delete=models.CASCADE)
    company = models.ForeignKey("Company", related_name="rider", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    visibility = models.CharField(choices=Visibility.choices(), default=Visibility.ONLINE)


class Company(TimestampMixin, VerificationMixin, models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    owner = models.ForeignKey(User, related_name="company", on_delete=models.CASCADE)
    name = models.CharField(_("Comapny name"), max_length=600)
    
    fleets = models.ManyToManyField("Fleet", related_name="company")
    offices = ArrayField(models.CharField(_("Company offices"), max_length=500), size=2, default=list)

    rc_num = models.CharField(_("RC Number"), null=True, blank=True)
    image = models.URLField(_("Business logo url"), default="")
    status = models.CharField(_("Account status"), choices=AccountStatus.choices(), default=AccountStatus.ACTIVE)
    overall_rating = models.IntegerField(_("Rating"), choices=Rating.choices(), null=True, blank=True)
    customers = models.ForeignKey(Business, related_name="company", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name

class Vehicle(TimestampMixin, VerificationMixin, models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    owner = models.ForeignKey(User, related_name="vehicle", on_delete=models.CASCADE)
    vehicle_type = models.CharField(_("Vehicle type"), choices=VehicleType.choices(), default=VehicleType.MOTORCYCLE)
    brand_and_model = models.CharField(_("Brand and model"), max_length=500)
    plate_number = models.CharField(_("Plate number"), max_length=10)

    def __str__(self) -> str:
        return self.brand_and_model + f"({self.vehicle_type})"

class Fleet(TimestampMixin, models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    owner = models.ForeignKey(User, related_name="fleet", on_delete=models.CASCADE)
    riders = models.ManyToManyField(CompanyRider, related_name="fleet")

    def __str__(self) -> str:
        return self.owner.email + "fleet"

# Note: Move to delivery app
class Saved(TimestampMixin, models.Model):
    pass

class Review(TimestampMixin, models.Model):
    pass

class Products(TimestampMixin, models.Model):
    pass