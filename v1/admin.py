from django.contrib import admin

from v1.models import *


# Register your models here.

@admin.register(CustomUser)
class CustomerUserModelAdmin(admin.ModelAdmin):
    list_display = ('phone_number','chat_id', 'is_active')
    search_fields = ('phone_number','chat_id')


@admin.register(QR)
class QRModelAdmin(admin.ModelAdmin):
    list_display = (
        'partner', 'qrc_id', 'terminal_ext_id', 'merchant_id', 'purpose', 'currency', 'min_amount', 'max_amount',
        'expire_date', 'created_date', 'is_active')

    search_fields = (
        'qrc_id', 'terminal_ext_id', 'merchant_id', 'purpose', 'currency', 'min_amount', 'max_amount',
        'expire_date', 'created_date', 'is_active')


@admin.register(Transaction)
class TransactionModelAdmin(admin.ModelAdmin):
    list_display = ('qr', 'trace_id', 'amount', 'status', 'description', 'created_at')
    search_fields = ('trace_id', 'amount', 'status', 'description', 'created_at')
