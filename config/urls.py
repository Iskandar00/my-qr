from django.contrib import admin
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from v1.views import qr_create, check, pay, RegisterView, LoginView, UserTerminalStatsView, TerminalListView, \
    TransactionListView, Last31DaysTransactionStatsView, MCCListView, MCCWithTerminalTotalsView, \
    TerminalLocationPurposeView

schema_view = get_schema_view(
    openapi.Info(
        title="My QR API",
        default_version='v1',
        description="API dokumentatsiyasi",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth
    path('api/v1/register/', RegisterView.as_view(), name='register'),
    path('api/v1/login/', LoginView.as_view(), name='login'),

    # QR API
    path('api/v1/create/', qr_create, name='qr_create'),
    path('api/v1/check/<str:qrc_id>/', check, name='qr_check'),
    path('api/v1/pay/', pay, name='qr_pay'),
    path('user-terminal-stats/', UserTerminalStatsView.as_view(), name='user-terminal-stats'),
    path('terminals/', TerminalListView.as_view(), name='terminal-list'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/last-31-days/', Last31DaysTransactionStatsView.as_view(), name='last-30-days-transactions'),
    path('api/mcc/', MCCListView.as_view(), name='mcc-list'),
    path('mcc-terminal-count/', MCCWithTerminalTotalsView.as_view(), name='mcc-terminal-count'),
    path('terminals/location-purpose/', TerminalLocationPurposeView.as_view(), name='terminal-location-purpose'),

    # Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]