from django.http import response
from rest_framework_simplejwt.exceptions import TokenError
from .test_helpers import AccountTestHelper
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch

from ..tasks import send_verification_mail


User = get_user_model()

# endpoints
REGISTER_BUSINESS_USER = reverse('accounts:business-user-sign-up')
LOGIN = reverse('accounts:login')

# token
REFRESH = reverse('accounts:token_refresh')
VERIFY = reverse('accounts:token_verify')

class RegisterBusinessUserTestCase(AccountTestHelper):

    def test_can_create_business_user(self):

        new_user = self.new_user
        response = self.client.post(REGISTER_BUSINESS_USER, new_user, format='json')
        self.assert_201_created(response, 'User not created')

    def test_cannot_create_user_without_first_and_last_name(self):

        new_user = self.new_user.copy()
        
        new_user.pop("first_name")
        new_user.pop("last_name")
        response = self.client.post(REGISTER_BUSINESS_USER, new_user, format='json')
        self.assert_400_bad(response, 'User was created without first and last name')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=new_user.get('email'))

        new_user = self.new_user.copy()

        new_user.pop("first_name")
        response = self.client.post(REGISTER_BUSINESS_USER, new_user, format='json')
        self.assert_400_bad(response, 'User was created without first name')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(first_name=new_user.get('first_name'))

        new_user = self.new_user.copy()

        new_user.pop("last_name")
        response = self.client.post(REGISTER_BUSINESS_USER, new_user, format='json')
        self.assert_400_bad(response, 'User was created without last name')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(last_name=new_user.get('last_name'))

    def test_cannot_create_user_without_email_or_phone(self):
        
        new_user = self.new_user
        new_user.pop("email")
        new_user.pop("phone_number")

        response = self.client.post(REGISTER_BUSINESS_USER, new_user, format='json')
        self.assert_400_bad(response, 'User was created without email or phone')

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(first_name=new_user.get("first_name"))

    @patch("accounts.tasks.send_verification_mail.delay")
    def test_no_verification_mail_sent_provided_email_and_phone(self, mock_email):

        new_user = self.new_user
        response = self.client.post(REGISTER_BUSINESS_USER, new_user, format='json')

        self.assert_201_created(response, 'User not created')
        mock_email.assert_not_called()

    @patch("accounts.tasks.send_verification_mail.delay")
    def test_verification_mail_sent_provided_email_only(self, mock_email):

        # just email
        new_user = self.new_user.copy()
        new_user.pop("phone_number")

        response = self.client.post(REGISTER_BUSINESS_USER, new_user, format='json')
        self.assert_201_created(response, 'User not created')
        mock_email.assert_called_once()

    @patch("accounts.tasks.send_verification_mail.delay")
    def test_verification_mail_sent_provided_phone_only(self, mock_email):

        # just phone
        new_user = self.new_user.copy()
        new_user.pop("email")

        response = self.client.post(REGISTER_BUSINESS_USER, new_user, format='json')
        self.assert_201_created(response, 'User not created')
        mock_email.assert_called_once()

    def test_can_create_business_user_without_business_info(self):

        new_user = self.new_user
        new_user.pop('business')

        response = self.client.post(REGISTER_BUSINESS_USER, new_user, format='json')
        self.assert_201_created(response, 'User not created')

    def test_cannot_create_business_without_required_fields_for_business_user(self):

        new_user = self.new_user
        new_user["business"].pop("address")
        new_user["business"].pop("city")
        new_user["business"].pop("state")

        response = self.client.post(REGISTER_BUSINESS_USER, new_user, format='json')
        self.assert_400_bad(response, 'Business was created without location')


class LoginTestCase(AccountTestHelper):
        
    def test_cannot_get_tokens_without_credentials(self):

        response = self.client.post(LOGIN, {}, format='json')
        self.assert_400_bad(response)

        # test user can get tokens
        user_data = self.get_user()
        login_data = {'email': user_data.email, 'password': self.test_password}

        response = self.client.post(LOGIN, data=login_data, format='json')
        
        self.assert_200_ok(response)
        token_data = response.json()
        self.assertIsNotNone(token_data.get('access')), self.assertIsNotNone(token_data.get('refresh'))


    def test_cannnot_refresh_token_without_token(self):
        user_data = self.get_user()
        print(User.objects.first().__dict__)
        login_data = {'email': user_data.email, 'password': self.test_password}
        print(login_data)
        response = self.client.post(LOGIN, data=login_data, format='json')
        self.assert_200_ok(response)
        access_token, refresh_token = response.json().get('access'), response.json().get('refresh')

        # refresh without token
        response = self.client.post(REFRESH, {}, format='json')
        self.assert_400_bad(response)

        # with token
        response = self.client.post(REFRESH, {'refresh': refresh_token}, format='json')
        self.assert_200_ok(response)
        self.assertNotEqual(access_token, response.json().get('access'))

    @patch('rest_framework_simplejwt.tokens.Token.for_user')
    def test_token_expiry(self, validate_mock):
        
        user_data = self.get_user()
        login_data = {'email': user_data.email, 'password': self.test_password}
        response = self.client.post(LOGIN, data=login_data, format='json')
        self.assert_200_ok(response)
        access_token, refresh_token = response.json().get('access'), response.json().get('refresh')

        # verify access token
        validate_mock.side_effect = TokenError(_("Token is invalid or expired"))
        response = self.client.post(VERIFY, {'token': access_token}, format='json')
        self.assert_401_unauthorized(response)

        # token expired
        validate_mock.side_effect = TokenError(_("Token is invalid or expired"))
        response = self.client.post(REFRESH, {'refresh': refresh_token}, format='json')
        self.assert_401_unauthorized(response)


class VerificationTestCase(AccountTestHelper): ...

