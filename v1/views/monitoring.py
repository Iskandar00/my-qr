from django.db.models import Sum, Count, Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFilter
from rest_framework import generics, filters
from datetime import timedelta
from datetime import datetime, time

from v1.models import Transaction, Terminal, CustomUser, MCC
from v1.serializers import TerminalStatsSerializer, TerminalSerializer, \
    TransactionSerializer, MCCSerializer, TerminalLocationPurposeSerializer


# ----------------------------------------
# USER TERMINAL STATS
# ----------------------------------------

class UserTerminalStatsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: TerminalStatsSerializer(many=True)})
    def get(self, request):
        user = request.user

        if user.is_superuser:
            # Umumiy summa (faqat Success bo‘yicha)
            overall_total = Terminal.objects.aggregate(
                summa=Sum('transactions__amount', filter=Q(transactions__status=1))
            )['summa'] or 0

            total_terminals = Terminal.objects.count()

            # Umumiy tranzaksiya statistikasi
            total_transactions = Transaction.objects.count()
            created_count = Transaction.objects.filter(status=0).count()
            success_count = Transaction.objects.filter(status=1).count()
            failed_count = Transaction.objects.filter(status=2).count()

            users_terminals = []
            for u in CustomUser.objects.all():
                user_terminals = Terminal.objects.filter(partner=u).annotate(
                    total_transactions=Count('transactions'),
                    total_amount=Sum('transactions__amount')
                )

                terminals_data = [
                    {
                        "name": t.name,
                        "purpose": t.purpose,
                        "total_transactions": t.total_transactions,
                        "total_amount": t.total_amount or 0
                    }
                    for t in user_terminals
                ]
                users_terminals.append({"user": u.id, "terminals": terminals_data})

            return Response({
                "total_amount": str(overall_total),
                "total_terminals": total_terminals,
                "total_transactions": total_transactions,
                "created_count": created_count,
                "success_count": success_count,
                "failed_count": failed_count,
                "users_terminals": users_terminals
            })

        # Oddiy foydalanuvchi uchun statistikalar
        terminals = Terminal.objects.filter(partner=user).annotate(
            total_transactions=Count('transactions', filter=Q(transactions__status=1)),
            total_amount=Sum('transactions__amount', filter=Q(transactions__status=1))
        )

        overall_total = terminals.aggregate(
            overall_total=Sum('transactions__amount', filter=Q(transactions__status=1))
        )['overall_total'] or 0

        # Foydalanuvchi tranzaksiyalari bo‘yicha statistikalar
        user_transactions = Transaction.objects.filter(qr__partner=user)
        total_transactions = user_transactions.count()
        created_count = user_transactions.filter(status=0).count()
        success_count = user_transactions.filter(status=1).count()
        failed_count = user_transactions.filter(status=2).count()

        serializer = TerminalStatsSerializer(terminals, many=True)
        return Response({
            "total_amount": str(overall_total),
            "total_transactions": total_transactions,
            "created_count": created_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "total_terminals": serializer.data
        })


# -----------------------------
# Transaction Filter
# -----------------------------
class TransactionFilter(FilterSet):
    created_from = DateFilter(field_name="created_at", lookup_expr='gte')
    created_to = DateFilter(field_name="created_at", lookup_expr='lte')

    class Meta:
        model = Transaction
        fields = ['status', 'qr', 'qr__partner', 'qr__partner__username', 'created_from', 'created_to']


# -----------------------------
# Terminal Filter
# -----------------------------
class TerminalFilter(FilterSet):
    created_from = DateFilter(field_name="created_date", lookup_expr='gte')
    created_to = DateFilter(field_name="created_date", lookup_expr='lte')

    class Meta:
        model = Terminal
        fields = ['status', 'qr_type', 'partner', 'currency', 'created_from', 'created_to']


# -----------------------------
# Terminal ListView
# -----------------------------
class TerminalListView(generics.ListAPIView):
    queryset = Terminal.objects.all().order_by('-created_date')
    serializer_class = TerminalSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TerminalFilter
    search_fields = ['name', 'purpose', 'address']
    ordering_fields = ['created_date', 'amount', 'name']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if not user.is_superuser:
            qs = qs.filter(partner=user)

        created_from = self.request.GET.get('created_from')
        created_to = self.request.GET.get('created_to')

        if created_from:
            start_date = datetime.combine(datetime.strptime(created_from, "%Y-%m-%d"), time.min)
            qs = qs.filter(created_date__gte=start_date)
        if created_to:
            end_date = datetime.combine(datetime.strptime(created_to, "%Y-%m-%d"), time.max)
            qs = qs.filter(created_date__lte=end_date)

        return qs


# -----------------------------
# Transaction ListView
# -----------------------------
class TransactionListView(generics.ListAPIView):
    queryset = Transaction.objects.all().order_by('-created_at')
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ['trace_id', 'description']
    ordering_fields = ['created_at', 'amount', 'status']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()

        if not user.is_superuser:
            qs = qs.filter(qr__partner=user)

        created_from = self.request.GET.get('created_from')
        created_to = self.request.GET.get('created_to')

        if created_from:
            start_date = datetime.combine(datetime.strptime(created_from, "%Y-%m-%d"), time.min)
            qs = qs.filter(created_at__gte=start_date)
        if created_to:
            end_date = datetime.combine(datetime.strptime(created_to, "%Y-%m-%d"), time.max)
            qs = qs.filter(created_at__lte=end_date)

        return qs


class Last31DaysTransactionStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        end_date = now().date()
        start_date = end_date - timedelta(days=30)  # Oxirgi 31 kun (bugungi kun bilan birga)

        # Foydalanuvchiga qarab querysetni cheklash
        qs = Transaction.objects.filter(created_at__date__range=(start_date, end_date))
        if not user.is_superuser:
            qs = qs.filter(qr__partner=user)

        # Kunlar bo‘yicha guruhlash
        stats = (
            qs.values('created_at__date')
            .annotate(
                total=Count('id'),
                created_count=Count('id', filter=Q(status=0)),
                success_count=Count('id', filter=Q(status=1)),
                failed_count=Count('id', filter=Q(status=2)),
            )
            .order_by('created_at__date')
        )

        # Formatlash (kun -> ma'lumot)
        result = []
        for day in stats:
            result.append({
                "date": day['created_at__date'],
                "total": day['total'],
                "created_count": day['created_count'],
                "success_count": day['success_count'],
                "failed_count": day['failed_count'],
            })

        return Response(result)


class MCCListView(generics.ListAPIView):
    queryset = MCC.objects.all().order_by('code')
    serializer_class = MCCSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['code']
    search_fields = ['description']
    ordering_fields = ['code', 'description']


class MCCWithTerminalTotalsView(APIView):
    def get(self, request):
        mcc_list = MCC.objects.annotate(
            terminal_count=Count('terminal'),
            total_transactions=Sum('terminal__transactions__amount'),
            transactions_count=Count('terminal__transactions')
        )

        data = [
            {
                "mcc_id": mcc.id,
                "code": mcc.code,
                "description": mcc.description,
                "terminal_count": mcc.terminal_count,
                "transactions_count": mcc.transactions_count,
                "transactions_total_amount": mcc.total_transactions or 0
            }
            for mcc in mcc_list
        ]

        return Response(data)

class TerminalLocationPurposeView(ListAPIView):
    queryset = Terminal.objects.all()
    serializer_class = TerminalLocationPurposeSerializer