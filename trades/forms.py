from django import forms
from .models import Trade

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Selecione um arquivo CSV")




class TradeFilterForm(forms.Form):
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Data Inicial"
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Data Final"
    )

    # Opções dinâmicas para moedas
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtém moedas únicas do banco de dados para os selects
        executed_coin_choices = Trade.objects.values_list('executed_coin', flat=True).distinct()
        amount_coin_choices = Trade.objects.values_list('amount_coin', flat=True).distinct()

        # Adiciona opção vazia e converte em lista de tuplas para dropdown
        self.fields['executed_coin'].choices = [('', 'Todas')] + [(coin, coin) for coin in executed_coin_choices if coin]
        self.fields['amount_coin'].choices = [('', 'Todas')] + [(coin, coin) for coin in amount_coin_choices if coin]

    executed_coin = forms.ChoiceField(
        required=False, 
        choices=[], 
        label="Moeda Executada"
    )

    amount_coin = forms.ChoiceField(
        required=False, 
        choices=[], 
        label="Moeda da Quantia"
    )

    side = forms.ChoiceField(
        required=False, 
        choices=[('', 'Todos'), ('BUY', 'Buy'), ('SELL', 'Sell')], 
        label="Tipo (Side)"
    )
