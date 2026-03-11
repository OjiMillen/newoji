
from django.contrib import admin

from .models import *
# Register your models here.
from django.utils.html import format_html

from django.db import models
import uuid
from bankingsystem.admin_actions import export_as_csv

class LoanRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'credit_facility', 'payment_tenure', 'amount', 'requested_at']
    list_filter = ['credit_facility', 'payment_tenure', 'requested_at']
    search_fields = ['user__email', 'amount', 'reason']
    readonly_fields = ['user', 'requested_at']
    
    fieldsets = (
        ('Loan Details', {
            'fields': ('user', 'credit_facility', 'payment_tenure', 'amount', 'reason')
        }),
        ('Additional Information', {
            'fields': ('requested_at',)
        })
    )

admin.site.register(LoanRequest, LoanRequestAdmin)



class PayBillsAdmin(admin.ModelAdmin):
    list_display = ['user', 'address1', 'city', 'state', 'zipcode', 'nickname', 'delivery_method', 'amount', 'get_date', 'status']
    list_filter = ['delivery_method', 'status']
    search_fields = ['user__username', 'address1', 'city', 'state', 'zipcode', 'nickname']
    ordering = ['-timestamp']
    actions = ['mark_as_paid', 'mark_as_cancelled']

    def get_date(self, obj):
        return f"{obj.year}-{obj.month:02d}-{obj.day:02d}"

    get_date.short_description = 'Date of Delivery'

    def mark_as_paid(self, request, queryset):
        rows_updated = queryset.update(status='completed')
        if rows_updated == 1:
            message_bit = "1 record was"
        else:
            message_bit = f"{rows_updated} records were"
        self.message_user(request, f"{message_bit} successfully marked as paid.")

    mark_as_paid.short_description = "Mark selected bills as paid"

    def mark_as_cancelled(self, request, queryset):
        rows_updated = queryset.update(status='cancelled')
        if rows_updated == 1:
            message_bit = "1 record was"
        else:
            message_bit = f"{rows_updated} records were"
        self.message_user(request, f"{message_bit} successfully marked as cancelled.")

    mark_as_cancelled.short_description = "Mark selected bills as cancelled"

admin.site.register(PayBills, PayBillsAdmin)

class CardDetailAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_type', 'masked_card_number', 'expiry_month', 'expiry_year', 'card_owner', 'timestamp')
    search_fields = ('user__username', 'card_number', 'card_owner')
    list_filter = ('card_type', 'timestamp')

    def masked_card_number(self, obj):
        return f"**** **** **** {obj.card_number[-4:]}"

    masked_card_number.short_description = 'Card Number'

admin.site.register(CardDetail, CardDetailAdmin)

class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_email', 'amount', 'recipient_account', 'date', 'status', 'current_balance')
    list_filter = ('status', )
    search_fields = ('user__email', 'user__username')

    # Allow date and timestamp to be edited
    fields = ('user', 'target', 'bank_sort_code', 'swift_code', 'recipient_bank_name', 
              'description', 'account_number', 'amount', 'status', 'date', 'timestamp')

    
    def client_name(self, obj):
        return obj.user.get_full_name()
    client_name.short_description = 'Client Name'
    
    def client_email(self, obj):
        return obj.user.email
    client_email.short_description = 'Client Email'
    
    def recipient_account(self, obj):
        return obj.target
    recipient_account.short_description = 'Recipient Account'
    
    def current_balance(self, obj):
        deposits = obj.user.deposits.aggregate(models.Sum('amount'))['amount__sum'] or 0
        withdrawals = obj.user.withdrawals.aggregate(models.Sum('amount'))['amount__sum'] or 0
        balance = deposits - withdrawals
        return balance
    current_balance.short_description = 'Current Balance'
    
admin.site.register(Withdrawal, WithdrawalAdmin)



"""
class CryptoWITHDRAWAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_method', 'amount', 'status', 'date')
    list_filter = ('status', 'payment_method')
    search_fields = ('user__username', 'user__email')

    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and form.cleaned_data['status'] == 'COMPLETE':
            obj.update_balance()
        obj.save()

admin.site.register(CryptoWITHDRAW, CryptoWITHDRAWAdmin)

"""


class CRYPWALLETSAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Bitcoin', {
            'fields': ('bitcoin', 'bitcoin_qr_code_preview', 'bitcoin_qr_code'),
            'description': 'Enter and manage Bitcoin wallet details.'
        }),
        ('Ethereum', {
            'fields': ('ethereum', 'ethereum_qr_code_preview', 'ethereum_qr_code'),
            'description': 'Enter and manage Ethereum wallet details.'
        }),

        ('USDT ERC20', {
            'fields': ('usdt_erc20', 'usdt_erc20_qr_code_preview', 'usdt_erc20_qr_code'),
            'description': 'Enter and manage usdt_erc20 wallet details.'
        }),
        ('Tron', {
            'fields': ('tron', 'tron_qr_code_preview', 'tron_qr_code'),
            'description': 'Enter and manage Tron wallet details.'
        }),
    )
    
    readonly_fields = (
        'bitcoin_qr_code_preview',
        'ethereum_qr_code_preview',
        'usdt_erc20_qr_code_preview',
        'tron_qr_code_preview',
    )

    def bitcoin_qr_code_preview(self, obj):
        if obj.bitcoin_qr_code:
            return format_html('<img src="{}" style="width: 100px; height: 100px;" />', obj.bitcoin_qr_code.url)
        return "No QR Code"
    bitcoin_qr_code_preview.short_description = "Bitcoin QR Code"

    def ethereum_qr_code_preview(self, obj):
        if obj.ethereum_qr_code:
            return format_html('<img src="{}" style="width: 100px; height: 100px;" />', obj.ethereum_qr_code.url)
        return "No QR Code"
    ethereum_qr_code_preview.short_description = "Ethereum QR Code"



    def usdt_erc20_qr_code_preview(self, obj):
        if obj.usdt_erc20_qr_code:
            return format_html('<img src="{}" style="width: 100px; height: 100px;" />', obj.usdt_erc20_qr_code.url)
        return "No QR Code"
    usdt_erc20_qr_code_preview.short_description = "usdt_erc20 QR Code"

    def tron_qr_code_preview(self, obj):
        if obj.tron_qr_code:
            return format_html('<img src="{}" style="width: 100px; height: 100px;" />', obj.tron_qr_code.url)
        return "No QR Code"
    tron_qr_code_preview.short_description = "Tron QR Code"

admin.site.register(CRYPWALLETS, CRYPWALLETSAdmin)



@admin.register(MailSubscription)
class MailSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed')
    search_fields = ('email',)
    list_filter = ('date_subscribed',)


@admin.register(BankTransfer)

class BankTransferAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Payment Method Details', {
            'fields': ('method', 'name_tag'),
            'description': 'Specify the payment method and its associated identifier.'
        }),
        ('QR Code Image', {
            'fields': ('qr_code_image_preview', 'qr_code_image'),
            'description': 'Upload or manage the QR code image for the payment method.'
        }),
        # 'Bank Image' section removed
    )

    readonly_fields = ('qr_code_image_preview', 'bank_image_preview')
    list_display = ('method', 'name_tag', 'qr_code_image_preview', 'bank_image_preview')
    search_fields = ('method', 'name_tag')
    list_filter = ('method',)

    def qr_code_image_preview(self, obj):
        if obj.qr_code_image:
            return format_html('<img src="{}" style="width: 100px; height: 100px;" />', obj.qr_code_image.url)
        return "No QR Code"
    qr_code_image_preview.short_description = "QR Code Preview"

    def bank_image_preview(self, obj):
        if obj.bank_image:
            return format_html('<img src="{}" style="width: 100px; height: 100px;" />', obj.bank_image.url)
        return "No Bank Image"
    bank_image_preview.short_description = "Bank Image Preview"
    


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_method', 'amount', 'status', 'date', 'timestamp')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('user__username', 'payment_method', 'status', 'amount')
    ordering = ('-date',)
    date_hierarchy = 'date'
    
    # Read-only fields
    readonly_fields = ('date', 'timestamp')

    fieldsets = (
        (None, {
            'fields': ('user', 'payment_method', 'amount', 'giftcard_type', 'giftcard_code', 'bank_transfer', 'status')
        }),
        ('Dates', {
            'fields': ('date', 'timestamp'),
            'classes': ('collapse',)  # Make this section collapsible
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Custom save logic (if needed)
        super().save_model(request, obj, form, change)

admin.site.register(Payment, PaymentAdmin)

admin.site.add_action(export_as_csv, name='export_selected')

admin.site.register(SUPPORT)
