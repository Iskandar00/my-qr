from django.contrib import admin

from v1.models import *


# Register your models here.

@admin.register(CustomUser)
class CustomerUserModelAdmin(admin.ModelAdmin):
    list_display = ('phone_number','chat_id', 'is_active')
    search_fields = ('phone_number','chat_id')


# MCC admin
@admin.register(MCC)
class MCCAdmin(admin.ModelAdmin):
    list_display = ('code', 'description')
    search_fields = ('code', 'description')
    list_display_links = list_display


# Terminal admin
@admin.register(Terminal)
class TerminalAdmin(admin.ModelAdmin):
    list_display = (
        'ext_id', 'partner', 'qr_type', 'status', 'amount', 'min_amount',
        'max_amount', 'currency', 'purpose', 'name', 'mcc', 'created_date', 'expire_date', 'is_active'
    )
    list_display_links = list_display
    list_filter = ('qr_type', 'status', 'currency', 'is_active', 'mcc')
    search_fields = ('ext_id', 'partner__username', 'purpose', 'name', 'address', 'mcc__description')

@admin.register(Transaction)
class TransactionModelAdmin(admin.ModelAdmin):
    list_display = ('qr', 'trace_id', 'amount', 'status', 'description', 'created_at')
    search_fields = ('trace_id', 'amount', 'status', 'description', 'created_at')
