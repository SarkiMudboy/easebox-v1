import factory
from django.contrib.auth import get_user_model
# from django.contrib.auth.hashers import make_password
from ..models import Business

User = get_user_model()

CATEGORIES = ['CLOTHING', 'FOOD', 'GADGETS', 'JEWELRIES', 'TRANSPORT']

class BusinessFactory(factory.django.DjangoModelFactory):
    
    class Meta:
        model = Business

    name = 'Andre sports'
    address = factory.Faker("address")
    city = "ILORIN"
    state = "KWARA"
    category = factory.Iterator(CATEGORIES)


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User
    
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.LazyAttribute(lambda user: "%s_%s@examplemail.com" %(user.first_name, user.last_name))
    phone_number = factory.Sequence(lambda n: '0908990999%d' %n)
    password = 'its-a-secret'
    accept_terms_and_privacy = True

    @classmethod
    @property
    def raw_password(self):
        return "its-a-secret"
    

    