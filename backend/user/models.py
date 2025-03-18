from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
import uuid
from institution.models import Institution
from .validation import nationalId_length_validation
from django.contrib.auth.hashers import make_password

# Create your models here.


class CustomManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not specified a valid email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_teacher", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_valid", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_teacher", False)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_valid", True)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255, blank=False, null=False)
    last_name = models.CharField(max_length=255, blank=False, null=False)
    avatar = models.ImageField(
        upload_to='uploads/user/avatars', blank=True, null=True)
    is_teacher = models.BooleanField(default=False)
    national_id = models.CharField(
        max_length=14, blank=False, null=False, validators=[nationalId_length_validation])
    instituition = models.ForeignKey(
        Institution, on_delete=models.CASCADE, null=True, related_name="institution")

    # Authentication fields
    is_active = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # Email verification
    email_verification_code = models.CharField(
        max_length=6, blank=True, null=True)
    email_verification_code_expiry = models.DateTimeField(
        blank=True, null=True)

    # Social login information
    google_id = models.CharField(max_length=255, blank=True, null=True)

    # Timestamps
    data_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        role = "admin" if self.is_superuser else "teacher" if self.is_teacher else "student"
        return f"{self.full_name} ({role})"

    def save(self, **fields):
        if 'password' in fields or (not self.id and self.password):
            self.password = make_password(self.password)
        return super().save(**fields)
