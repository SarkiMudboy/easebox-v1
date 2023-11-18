from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.db import transaction

User = get_user_model()

# Helos is from attack on titan (idk, name looks cool) 


class UserTestCase(TestCase):
    
    def test_create_user_with_email(self):

        user = None

        user = User.objects.create_user(
            first_name="Helos",
            last_name="Melly",
            email="test@user.com",
            password="foo"
        )

        self.assertIsNotNone(user)

        try:
            self.assertNone(user.phone_number)
        except AttributeError:
            pass

        self.assertEqual(user.first_name, "Helos")
        self.assertEqual(user.last_name, "Melly")
        self.assertEqual(user.email, "test@user.com")
        

    def test_create_user_with_phone(self):

        user = None

        user = User.objects.create_user(
            first_name="Helos",
            last_name="Melly",
            phone_number="+2348134567890",
            password="foo"
        )

        self.assertIsNotNone(user)

        try:
            self.assertNone(user.email)
        except AttributeError:
            pass

        self.assertEqual(user.first_name, "Helos")
        self.assertEqual(user.last_name, "Melly")
        self.assertEqual(user.phone_number, "+2348134567890")

    def test_create_user_with_email_and_phone_number(self):

        user = None

        user = User.objects.create_user(
            first_name="Helos",
            last_name="Melly",
            email="test@user.com",
            phone_number="+2348134567890",
            password="foo"
        )

        self.assertIsNotNone(user)

        self.assertEqual(user.first_name, "Helos")
        self.assertEqual(user.last_name, "Melly")
        self.assertEqual(user.email, "test@user.com")
        self.assertEqual(user.phone_number, "+2348134567890")

    def test_cannot_create_user_without_both_email_and_phone_number(self):

        user = None

        with self.assertRaises(ValueError):     
            User.objects.create_user(
                first_name="Helos",
                last_name="Melly",
                password="foo"
            )

        with self.assertRaises(ValueError):     
            User.objects.create_user(
                first_name="Helos",
                last_name="Melly",
                email="",
                phone_number="",
                password="foo"
            )


    def test_cannot_create_user_without_both_first_and_last_name(self):

        user = None

        with self.assertRaises(ValueError):     
            User.objects.create_user(
                first_name="",
                last_name="Melly",
                email="test@mail.com",
                phone_number="234567890",
                password="foo"
            )

        with self.assertRaises(ValueError):     
            User.objects.create_user(
                first_name="Helos",
                last_name="",
                email="test@mail.com",
                phone_number="234567890",
                password="foo"
            )

        with self.assertRaises(ValueError):     
            User.objects.create_user(
                first_name="",
                last_name="",
                email="test@mail.com",
                phone_number="234567890",
                password="foo"
            )

    def test_cannot_create_user_with_existing_email_or_phone_number(self):

        user = None

        user = User.objects.create_user(
            first_name="Helos",
            last_name="Melly",
            email="test@user.com",
            phone_number="+2348134567890",
            password="foo"
        )

        self.assertIsNotNone(user)

        with self.assertRaises(IntegrityError) as context:

            with transaction.atomic():
                User.objects.create_user(
                    first_name="Helos",
                    last_name="Melly",
                    email="test@user.com",
                    password="foo",
                )

        with self.assertRaises(IntegrityError) as context:
            
            with transaction.atomic():
                User.objects.create_user(
                    first_name="Helos",
                    last_name="Melly",
                    phone_number="+2348134567890",
                    password="foo",
                )

        # test should pass and not throw IntegrityError
        User.objects.create_user(
            first_name="Helos",
            last_name="Melly",
            phone_number="+2348135465",
            password="foo",
        )

        self.assertEqual(User.objects.count(), 2)

        # test should pass and not throw IntegrityError
        User.objects.create_user(
            first_name="Helos",
            last_name="Melly",
            email="test@mail.com",
            password="foo",
        )

        self.assertEqual(User.objects.count(), 3)


        