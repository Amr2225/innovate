from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from nanoid_field import NanoidField
from django.core.exceptions import ValidationError
from .validation import nationalId_length_validation
import uuid

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

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        # TODO: may be changed
        extra_fields.setdefault('is_email_verified', True)
        extra_fields.setdefault("role", "Admin")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    Role = [
        ("Institution", "Institution"),
        ("Student", "Student"),
        ("Teacher", "Teacher"),
        ("Admin", "Admin"),
    ]

    # Common Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, null=True, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_expiry_time_minutes = models.PositiveSmallIntegerField(default=5)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=15, choices=Role, default="Student")
    is_email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    # User Fields
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(
        upload_to='user/avatars', blank=True, null=True)
    birth_date = models.DateTimeField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    national_id = models.CharField(
        max_length=14, blank=True, null=True, unique=False, validators=[nationalId_length_validation])
    semester = models.PositiveSmallIntegerField(default=1)

    # Institution Fields
    SCHOOL = 'school'
    FACULTY = 'faculty'
    TYPE_CHOICES = [
        (SCHOOL, 'School'),
        (FACULTY, 'Faculty'),
    ]
    institution_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, null=True, blank=True,
        help_text="This field is required")

    access_code = NanoidField(max_length=8, blank=True,
                              null=True, unique=True, editable=True)
    name = models.CharField(max_length=255, blank=True,
                            null=True, unique=True)
    credits = models.PositiveIntegerField(blank=True, null=True)
    logo = models.ImageField(
        upload_to='institution/logo/', null=True, blank=True)

    # Relation
    institution = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name="members", limit_choices_to={"role": "Institution"})

    objects = CustomManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'middle_name', 'last_name']

    @property
    def full_name(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}"

    @property
    def level(self):
        if self.semester:
            return (self.semester + 1) // 2
        return None

    # def clean(self):
    #     super().clean()
    #     if self.role == "Institution" and not self.institution_type:
    #         raise ValidationError(
    #             "Institution type is required for institutions")

    def __str__(self):
        if self.role == "Institution":
            return f"{self.name} - {self.credits}"
        return f"{self.full_name} ({self.role})"

    def clean(self):
        super().clean()
        if self.role == "Institution" and not self.institution_type:
            raise ValidationError({
                'institution_type': 'This field is required'
            })
