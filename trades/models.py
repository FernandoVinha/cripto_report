from django.db import models

class Trade(models.Model):
    SIDE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    date = models.DateTimeField()  # Agora vamos salvar a data correta do CSV
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    price = models.DecimalField(max_digits=20, decimal_places=8)
    executed = models.DecimalField(max_digits=20, decimal_places=8)
    executed_coin = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    amount_coin = models.CharField(max_length=10)
    fee = models.DecimalField(max_digits=20, decimal_places=8)
    fee_coin = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.side} {self.executed} {self.executed_coin} at {self.price} {self.amount_coin}"
