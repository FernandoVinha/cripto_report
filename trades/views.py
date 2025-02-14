import csv
import re
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum, Avg, F
from .models import Trade
from .forms import CSVUploadForm, TradeFilterForm
import yfinance as yf
import json  # Adicionado para garantir formato correto dos dados no template


def extract_value_and_currency(value):
    """ Separa números e letras em valores monetários. """
    if not value:
        return 0.0, ""
    
    match = re.match(r"([\d\.\,]+)([A-Za-z]+)", value)
    if match:
        number = match.group(1).replace(',', '')  # Removendo vírgulas caso existam
        return float(number), match.group(2)  # Retorna número e moeda separadamente
    return 0.0, ""  # Retorna 0.0 se não conseguir separar


def upload_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']

            if not csv_file.name.endswith('.csv'):
                messages.error(request, "O arquivo precisa ser um CSV.")
                return redirect('upload_csv')

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file, delimiter=';')

            for row in reader:
                executed_value, executed_coin = extract_value_and_currency(row.get('Executed', ''))
                amount_value, amount_coin = extract_value_and_currency(row.get('Amount', ''))
                fee_value, fee_coin = extract_value_and_currency(row.get('Fee', ''))

                try:
                    date_parsed = datetime.strptime(row.get('Date(UTC)'), "%Y-%m-%d %H:%M:%S")
                except ValueError as e:
                    messages.error(request, f"Erro ao processar data '{row.get('Date(UTC)')}' na linha: {row}. Erro: {str(e)}")
                    continue

                Trade.objects.create(
                    date=date_parsed,
                    side=row.get('Side'),
                    price=float(row.get('Price', 0)),
                    executed=executed_value,
                    executed_coin=executed_coin,
                    amount=amount_value,
                    amount_coin=amount_coin,
                    fee=fee_value,
                    fee_coin=fee_coin,
                )

            messages.success(request, "CSV importado com sucesso!")
            return redirect('upload_csv')

    else:
        form = CSVUploadForm()

    return render(request, 'upload_csv.html', {'form': form})





def filter_trades(request):
    form = TradeFilterForm(request.GET)
    executed_coin = request.GET.get('executed_coin', "ALL")
    amount_coin = request.GET.get('amount_coin', "ALL")
    trades = Trade.objects.all().order_by("date")

    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')

        if start_date:
            trades = trades.filter(date__gte=datetime.combine(start_date, datetime.min.time()))
        if end_date:
            trades = trades.filter(date__lte=datetime.combine(end_date, datetime.max.time()))

        if executed_coin and executed_coin != "ALL":
            trades = trades.filter(executed_coin=executed_coin)

        if amount_coin and amount_coin != "ALL":
            trades = trades.filter(amount_coin=amount_coin)

    # Captura moedas disponíveis no banco
    available_executed_coins = Trade.objects.values_list('executed_coin', flat=True).distinct()
    available_amount_coins = Trade.objects.values_list('amount_coin', flat=True).distinct()

    total_buy_volume = trades.filter(side='BUY').aggregate(Sum('executed'))['executed__sum'] or 0
    total_sell_volume = trades.filter(side='SELL').aggregate(Sum('executed'))['executed__sum'] or 0
    average_price = trades.aggregate(Avg('price'))['price__avg'] or 0

    # Preço médio de compra
    buy_trades = trades.filter(side="BUY")
    total_asset = buy_trades.aggregate(Sum('executed'))['executed__sum'] or 0
    total_cost = buy_trades.aggregate(total=Sum(F('price') * F('executed')))['total'] or 0
    avg_buy_price = float(total_cost) / float(total_asset) if total_asset > 0 else 0

    # Pegando preço atual do ativo
    asset_price_now = 0
    if executed_coin and executed_coin != "ALL":
        try:
            asset_price_now = float(yf.Ticker(f"{executed_coin}-USD").history(period="1d")['Close'].iloc[-1])
        except IndexError:
            asset_price_now = 0
        except Exception as e:
            messages.error(request, f"Erro ao buscar preço de {executed_coin}: {str(e)}")

    # Lucro em USD
    usd_gain = (float(asset_price_now) - float(avg_buy_price)) * float(total_asset) if total_asset > 0 and executed_coin and executed_coin != "ALL" else 0

    # 🔥 GARANTINDO QUE OS DADOS PARA O GRÁFICO ESTEJAM NO FORMATO JSON 🔥
    trade_dates = json.dumps([trade.date.strftime('%Y-%m-%d %H:%M') for trade in trades])
    trade_prices = json.dumps([float(trade.price) for trade in trades])
    trade_volumes = json.dumps([float(trade.executed) for trade in trades])

    return render(request, 'filter_trades.html', {
        'form': form,
        'executed_coin': executed_coin,
        'amount_coin': amount_coin,
        'available_executed_coins': available_executed_coins,
        'available_amount_coins': available_amount_coins,
        'total_buy_volume': total_buy_volume,
        'total_sell_volume': total_sell_volume,
        'average_price': average_price,
        'avg_buy_price': avg_buy_price,
        'asset_price_now': asset_price_now,
        'usd_gain': usd_gain,
        'trade_dates': trade_dates,  # 🚀 AGORA PASSA COMO JSON 🚀
        'trade_prices': trade_prices,  # 🚀
        'trade_volumes': trade_volumes  # 🚀
    })
