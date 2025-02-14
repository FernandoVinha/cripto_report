from django.urls import path
from .views import upload_csv, filter_trades

urlpatterns = [
    path('csv/', upload_csv, name='upload_csv'),
    path('', filter_trades, name='filter_trades'),
]
