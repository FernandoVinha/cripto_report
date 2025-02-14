from django.contrib import admin
from .models import Trade

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ('date', 'side', 'price', 'executed', 'executed_coin', 'amount', 'amount_coin', 'fee', 'fee_coin')
    list_filter = ('side', 'executed_coin', 'amount_coin', 'fee_coin', 'date')
    search_fields = ('executed_coin', 'amount_coin', 'fee_coin')
    ordering = ('-date',)

