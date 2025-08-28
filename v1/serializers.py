from django.contrib.auth import get_user_model, authenticate
from .models import Terminal, Transaction, MCC
import uuid
from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from v1.models import Terminal

User = get_user_model()


# ----------------------------------------
# REGISTER
# ----------------------------------------
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['phone_number', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            phone_number=validated_data['phone_number'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


# ----------------------------------------
# LOGIN
# ----------------------------------------
class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(phone_number=data['phone_number'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Phone number or password not valid")
        data['user'] = user
        return data


class MCCSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCC
        fields = ['id', 'code', 'description']


# ----------------------------------------
# QR SERIALIZER
# ----------------------------------------

class QRSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    min_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    max_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    expire_date = serializers.DateTimeField(required=False, allow_null=True)

    mcc = serializers.PrimaryKeyRelatedField(queryset=MCC.objects.all(), required=True)

    class Meta:
        model = Terminal
        fields = [
            "qr_type", "amount", "min_amount", "max_amount", "expire_date",
            "ext_id", "purpose", "currency", "name", "mcc", "address",
            "latitude", "longitude"
        ]

    def validate(self, attrs):
        qr_type = attrs.get('qr_type')
        expire_date = attrs.get('expire_date')
        amount = attrs.get('amount')
        min_amount = attrs.get('min_amount')
        max_amount = attrs.get('max_amount')

        # ✅ DYNAMIC QR shartlari
        if qr_type == "DYNAMIC":
            if amount is None:
                raise serializers.ValidationError({"amount": "Amount required for DYNAMIC QR"})

        # ✅ STATIC QR shartlari
        if qr_type == "STATIC":
            if expire_date:
                raise serializers.ValidationError({"expire_date": "Expire date should not be set for STATIC QR"})
            if min_amount is None:
                raise serializers.ValidationError({"min_amount": "min_amount is required for STATIC QR"})
            if max_amount is None:
                raise serializers.ValidationError({"max_amount": "max_amount is required for STATIC QR"})

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None

        qr_type = validated_data.get('qr_type')

        # ✅ DYNAMIC QR uchun min_amount va max_amount avtomatik o'rnatish
        if qr_type == "DYNAMIC":
            validated_data['min_amount'] = validated_data['amount']
            validated_data['max_amount'] = validated_data['amount']

            # Agar expire_date berilmagan bo‘lsa, 3 minut qo‘shamiz
            if not validated_data.get('expire_date'):
                validated_data['expire_date'] = timezone.now() + timedelta(minutes=3)

        # ✅ STATIC QR uchun amount ixtiyoriy, bo‘lmasa default 0
        if qr_type == "STATIC":
            validated_data['amount'] = validated_data.get('amount') or 0

        return Terminal.objects.create(partner=user, **validated_data)


# ----------------------------------------
# PAY SERIALIZER
# ----------------------------------------
class PaySerializer(serializers.Serializer):
    trace_id = serializers.CharField()
    amount = serializers.FloatField()


# ----------------------------------------
# TERMINAL STATS SERIALIZER
# ----------------------------------------
class TerminalStatsSerializer(serializers.ModelSerializer):
    total_transactions = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Terminal
        fields = ['id', 'name', 'purpose', 'total_transactions', 'total_amount']


# -----------------------------
# Transaction serializer (nested Terminal inside if needed)
# -----------------------------
class TerminalForTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terminal
        fields = '__all__'  # Barcha terminal fieldlari


class TransactionSerializer(serializers.ModelSerializer):
    qr = TerminalForTransactionSerializer(read_only=True)  # Terminal nested

    class Meta:
        model = Transaction
        fields = ['id', 'trace_id', 'amount', 'status', 'description', 'created_at', 'qr']


# -----------------------------
# Terminal serializer (nested Transactions inside)
# -----------------------------
class TransactionForTerminalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'trace_id', 'amount', 'status', 'description', 'created_at']


class TerminalSerializer(serializers.ModelSerializer):
    transactions = TransactionForTerminalSerializer(many=True, read_only=True)
    mcc = MCCSerializer(read_only=True)

    class Meta:
        model = Terminal
        fields = '__all__'

class TerminalLocationPurposeSerializer(serializers.ModelSerializer):
    location_and_purpose = serializers.SerializerMethodField()

    class Meta:
        model = Terminal
        fields = ['id', 'location_and_purpose']

    def get_location_and_purpose(self, obj):
        return {
            "latitude": obj.latitude,
            "longitude": obj.longitude,
            "purpose": obj.purpose,
            "address": obj.address
        }


