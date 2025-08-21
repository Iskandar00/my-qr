import uuid
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

from .models import QR, Transaction

User = get_user_model()


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


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(phone_number=data['phone_number'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Telefon raqam yoki parol noto'g'ri")
        data['user'] = user
        return data


class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model = QR
        fields = ['id', 'terminal_ext_id', 'purpose', 'currency', 'min_amount', 'max_amount', 'expire_date']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['qrc_id'] = str(uuid.uuid4()).replace('-', '')[:12]
        return QR.objects.create(partner=user, **validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['trace_id', 'qr', 'amount']
