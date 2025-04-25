from django.db import models

# Python
import uuid

# Django
from users.models import User


class Plan(models.Model):
    class Type(models.TextChoices):
        GOLD = "GOLD", "Gold"
        SILVER = "SILVER", "Silver"
        DIAMOND = "DIAMOND", "Diamond"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency = models.CharField(max_length=3)
    credit_value = models.PositiveIntegerField()
    students_limit = models.PositiveIntegerField()
    type = models.CharField(max_length=10, choices=Type.choices, unique=True)
    description = models.TextField()
    credit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"1 Credit = {self.students_limit} Students ({self.credit_price} {self.currency})"


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='institution_payments', limit_choices_to={"role": "Institution"})
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name='plans')
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    is_current = models.BooleanField(default=True)
    credits_amount = models.PositiveIntegerField()
    paymob_url = models.URLField(null=True, blank=True)
    payment_status = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.institution.name} - {self.plan.type} - {self.valid_from} to {self.valid_to} Current: {self.is_current}"


class Offer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    discount_percentage = models.PositiveIntegerField()
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name='plans', to_field='type')
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.discount_percentage}% off for {self.plan.type}"
