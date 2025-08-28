from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    chat_id = models.CharField(max_length=128, null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.phone_number

class MCC(models.Model):
    code = models.PositiveIntegerField(unique=True)
    description = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.code} - {self.description}"


class Terminal(models.Model):
    QR_TYPE_CHOICES = (
        ("STATIC", "Static"),
        ("DYNAMIC", "Dynamic")
    )

    STATUS_CHOICES = (
        ("ACTIVE", "Active"),
        ("USED", "Used"),
        ("EXPIRED", "Expired"),
        ("INACTIVE", "Inactive"),
    )


    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default="ACTIVE")
    qr_type = models.CharField(max_length=8, choices=QR_TYPE_CHOICES)

    ext_id = models.CharField(max_length=100, unique=True)

    partner = models.ForeignKey(CustomUser, on_delete=models.PROTECT)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    purpose = models.CharField(max_length=250)
    currency = models.CharField(max_length=50)
    name = models.CharField(max_length=120)
    mcc = models.ForeignKey(MCC, on_delete=models.SET_NULL, null=True)

    address = models.CharField(max_length=255, blank=True)
    latitude = models.CharField(max_length=250, blank=True)
    longitude = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return f"{self.purpose}"


class Transaction(models.Model):
    STATUS_CHOICES = (
        (0, 'Created'),
        (1, 'Success'),
        (2, 'Failed'),
    )

    qr = models.ForeignKey(Terminal, on_delete=models.SET_NULL, null=True, related_name='transactions')
    trace_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    description = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.trace_id

