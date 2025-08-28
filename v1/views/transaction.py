import asyncio
import uuid
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from v1.models import Transaction, Terminal
from v1.serializers import QRSerializer, PaySerializer, MCCSerializer
from v1.utils.telegram_utils import send_transaction_message


# ----------------------------------------
# CREATE QR
# ----------------------------------------
@swagger_auto_schema(method='POST', request_body=QRSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def qr_create(request):
    serializer = QRSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        instance = serializer.save()
        created_date = instance.created_date.strftime("%d-%m-%Y %H:%M:%S")
        expire_date = instance.expire_date.strftime("%d-%m-%Y %H:%M:%S") if instance.expire_date else None

        return Response({"data": {
            "partner": getattr(instance.partner, "username", None),
            "phone": getattr(instance.partner, "phone_number", None),
            "qrc_id": instance.ext_id,
            "purpose": instance.purpose,
            "currency": instance.currency,
            "min_amount": instance.min_amount,
            "max_amount": instance.max_amount,
            "amount": instance.amount,
            "created_date": created_date,
            "expire_date": expire_date,
            "qr_type": instance.qr_type,
            "name": instance.name,
            "mcc": MCCSerializer(instance.mcc).data,
            "address": instance.address,
            "latitude": instance.latitude,
            "longitude": instance.longitude,
        }}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ----------------------------------------
# CHECK QR
# ----------------------------------------
@swagger_auto_schema(
    method='GET',
    manual_parameters=[
        openapi.Parameter('trace_id', openapi.IN_QUERY, description="Trace ID", type=openapi.TYPE_STRING)]
)
@api_view(['GET'])
def check(request, qrc_id: str):
    trace_id = request.GET.get("trace_id") or str(uuid.uuid4())
    qr_obj = Terminal.objects.filter(ext_id=qrc_id).first()
    if not qr_obj:
        return Response({"error": "QR not found"}, status=status.HTTP_404_NOT_FOUND)

    if qr_obj.expire_date and qr_obj.expire_date < now():
        qr_obj.is_active = False
        qr_obj.status = "EXPIRED"
        qr_obj.save()

    if qr_obj.status in ['USED', 'EXPIRED', 'INACTIVE']:
        return Response({"error": f"QR status: {qr_obj.status}"}, status=status.HTTP_400_BAD_REQUEST)

    qr_transaction, _ = Transaction.objects.get_or_create(
        trace_id=trace_id,
        defaults={"qr": qr_obj, "status": 0, "description": "Created"}
    )

    data = {
        "qrc_id": qr_obj.ext_id,
        "trace_id": trace_id,
        "purpose": qr_obj.purpose,
        "currency": qr_obj.currency,
        "amount": qr_obj.amount,
        "min_amount": qr_obj.min_amount,
        "max_amount": qr_obj.max_amount,
        "status": qr_transaction.status,
        "description": qr_transaction.description,
    }

    return Response({"data": data}, status=status.HTTP_200_OK)


# ----------------------------------------
# PAY QR
# ----------------------------------------
@swagger_auto_schema(method='POST', request_body=PaySerializer)
@api_view(['POST'])
def pay(request):
    trace_id = request.data.get("trace_id")
    amount = request.data.get("amount")

    if not trace_id or amount is None:
        return Response({"error": "trace_id and amount required"}, status=status.HTTP_400_BAD_REQUEST)

    qr_transaction = Transaction.objects.filter(trace_id=trace_id).first()
    if not qr_transaction:
        return Response({"error": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    qr_obj = qr_transaction.qr
    if not qr_obj:
        return Response({"error": "QR not found"}, status=status.HTTP_404_NOT_FOUND)

    if qr_obj.qr_type == "DYNAMIC":
        amount = qr_obj.amount

    try:
        amount = float(amount)
    except ValueError:
        return Response({"error": "Invalid amount format"}, status=status.HTTP_400_BAD_REQUEST)

    if not qr_obj.is_active or amount < float(qr_obj.min_amount) or amount > float(qr_obj.max_amount):
        return Response({"error": "Invalid QR or amount"}, status=status.HTTP_400_BAD_REQUEST)

    if qr_obj.qr_type == "DYNAMIC":
        qr_obj.status = "USED"
        qr_obj.save()

    qr_transaction.amount = amount
    qr_transaction.status = 1
    qr_transaction.description = "Success"
    qr_transaction.save()

    user = qr_obj.partner
    if user and getattr(user, 'chat_id', None):
        asyncio.run(send_transaction_message(user.chat_id, trace_id, amount, qr_obj.purpose))

    return Response({"status": "SUCCESS", "trace_id": trace_id}, status=status.HTTP_200_OK)
