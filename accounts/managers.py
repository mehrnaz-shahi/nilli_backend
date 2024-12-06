from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with the given phone number and password.
        """
        User = get_user_model()
        if not email:
            raise ValueError('The email must be set')

        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Set the password for the user
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with the given phone number and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

