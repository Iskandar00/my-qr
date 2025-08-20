from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    is_active = models.BooleanField(default=True)
    chat_id = models.CharField(max_length=128, null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.phone_number


class QR(models.Model):
    partner = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    qrc_id = models.CharField(max_length=100, unique=True)
    terminal_ext_id = models.CharField(max_length=250)
    merchant_id = models.CharField(max_length=250)
    purpose = models.CharField(max_length=250)
    currency = models.CharField(max_length=50)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.qrc_id


class Transaction(models.Model):
    STATUS_CHOICES = (
        (0, 'Created'),
        (1, 'Success'),
        (2, 'Failed'),
    )

    qr = models.ForeignKey(QR, on_delete=models.SET_NULL, null=True)
    trace_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    description = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.trace_id
