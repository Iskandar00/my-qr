import asyncio
import uuid

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.utils.timezone import now
from v1.models import Transaction, QR
from v1.serializers import QRSerializer
from v1.utils.telegram_utils import send_transaction_message


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def qr_create(request):
    serializer = QRSerializer(data=request.data, context={'request': request})

    if serializer.is_valid():
        instance = serializer.save()

        created_date = instance.created_date.strftime("%d-%m-%Y %H:%M:%S")
        expire_date = instance.expire_date.strftime("%d-%m-%Y %H:%M:%S") if instance.expire_date else None

        return Response({"data": {
            "phone": instance.partner.phone_number,
            "qrc_id": instance.qrc_id,
            "purpose": instance.purpose,
            "currency": instance.currency,
            "min_amount": instance.min_amount,
            "max_amount": instance.max_amount,
            "created_date": created_date,
            "expire_date": expire_date,
        }}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def check(request, qrc_id: str):
    # currency = request.GET.get("currency")
    trace_id = request.GET.get("trace_id") or str(uuid.uuid4())

    qr_obj = QR.objects.filter(qrc_id=qrc_id).first()
    if not qr_obj:
        return Response({"error": "QR not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check expiration
    if qr_obj.expire_date and qr_obj.expire_date < now():
        qr_obj.is_active = False
        qr_obj.save()

    qr_transaction, created = Transaction.objects.get_or_create(
        trace_id=trace_id,
        defaults={"qr": qr_obj, "status": 0, "description": "Created"}
    )

    data = {
        "qrc_id": qr_obj.qrc_id,
        "trace_id": trace_id,
        "purpose": qr_obj.purpose,
        "currency": qr_obj.currency,
        "min_amount": qr_obj.min_amount,
        "max_amount": qr_obj.max_amount,
        "status": qr_transaction.status,
        "description": qr_transaction.description,
        "qr_status": "ACTIVE" if qr_obj.is_active else "NOT ACTIVE"
    }

    return Response({"data": data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def pay(request):
    trace_id = request.data.get("trace_id")
    amount = request.data.get("amount")

    if not all([amount, trace_id]):
        return Response({"error": "trace_id and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        amount = float(amount)
    except ValueError:
        return Response({"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)

    qr_transaction = Transaction.objects.filter(trace_id=trace_id).first()
    if not qr_transaction:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    qr_obj = qr_transaction.qr
    if not qr_obj.is_active:
        return Response({"error": "QR is not active"}, status=status.HTTP_400_BAD_REQUEST)

    if amount < float(qr_obj.min_amount) or amount > float(qr_obj.max_amount):
        return Response({
            "error": f"Amount must be between {qr_obj.min_amount} and {qr_obj.max_amount}"
        }, status=status.HTTP_400_BAD_REQUEST)

    qr_transaction.amount = amount
    qr_transaction.status = 4
    qr_transaction.description = "Success"
    qr_transaction.save()

    user = qr_transaction.qr.partner
    if user and user.chat_id:
        asyncio.run(send_transaction_message(user.chat_id, trace_id, amount,qr_transaction.qr.purpose))

    return Response({"status": "SUCCESS", "trace_id": trace_id}, status=status.HTTP_200_OK)
