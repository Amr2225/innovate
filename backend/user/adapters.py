from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for django-allauth to handle email-based authentication.
    """

    def populate_username(self, request, user):
        """
        Our User model doesn't use the username field, so we just pass.
        """
        pass

    def save_user(self, request, user, form, commit=True):
        """
        Custom save_user to handle username-less user model.
        """
        # Get user data from the form
        data = form.cleaned_data

        # Set the required fields
        user.email = data.get('email')
        user.first_name = data.get('first_name', '')
        user.last_name = data.get('last_name', '')

        # If we're handling a registration form with additional info
        if hasattr(form, 'cleaned_data') and 'national_id' in form.cleaned_data:
            user.national_id = form.cleaned_data.get('national_id', '')
        else:
            # Default national_id for email registration (will be updated later)
            user.national_id = '00000000000000'

        # Set the password if provided
        if 'password1' in data:
            user.set_password(data.get('password1'))

        # Save the user
        if commit:
            user.save()

        return user


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for django-allauth to handle social account connections.
    """

    def populate_user(self, request, sociallogin, data):
        """
        Populates a User model with data from the social account.
        """
        user = super().populate_user(request, sociallogin, data)

        # Set default values for required fields
        if sociallogin.account.provider == 'google':
            user.google_id = sociallogin.account.uid

        # Default national_id for social login (will be updated later)
        user.national_id = '00000000000000'

        # Activate user for social login
        user.is_active = True
        user.is_valid = True

        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Custom save_user to handle username-less user model with social login.
        """
        user = super().save_user(request, sociallogin, form)

        # Extra processing after user is saved
        if sociallogin.account.provider == 'google':
            user.google_id = sociallogin.account.uid
            user.is_active = True
            user.is_valid = True
            user.save()

        return user
