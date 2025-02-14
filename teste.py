import pandas as pd

# Lista de moedas conhecidas (criptomoedas + fiduciárias)
moedas = [
    "BTC", "ETH", "BNB", "USDT", "BUSD", "XRP", "ADA", "DOGE", "SOL", "DOT",
    "USD", "EUR", "BRL", "USDC", "LTC", "MATIC", "SHIB", "TRX", "AVAX"
]

def carregar_dados(caminho):
    """Carrega o arquivo CSV em um DataFrame."""
    return pd.read_csv(caminho)

def filtrar_trades(df, side=None, data_inicial=None, data_final=None, moeda_comprada=None, moeda_vendida=None):
    """Filtra os dados com base nos critérios fornecidos."""
    df_filtrado = df.copy()
    
    if side:
        df_filtrado = df_filtrado[df_filtrado['Side'] == side.upper()]
    
    if data_inicial and data_final:
        df_filtrado = df_filtrado[(df_filtrado['Date(UTC)'] >= data_inicial) & (df_filtrado['Date(UTC)'] <= data_final)]
    
    if moeda_comprada:
        df_filtrado = df_filtrado[df_filtrado['compra'] == moeda_comprada.upper()]
    
    if moeda_vendida:
        df_filtrado = df_filtrado[df_filtrado['venda'] == moeda_vendida.upper()]
    
    return df_filtrado

def calcular_totais(df):
    """Calcula os totais de gasto, recebido e custo médio."""
    df['Amount'] = df['Amount'].str.extract(r'([\d\.]+)').astype(float)
    df['Executed'] = df['Executed'].str.extract(r'([\d\.]+)').astype(float)
    df['Price'] = df['Amount'] / df['Executed']
    
    total_gasto = df['Amount'].sum()
    total_recebido = df['Executed'].sum()
    custo_medio = df['Price'].mean()
    
    return total_gasto, total_recebido, custo_medio

if __name__ == "__main__":
    caminho_arquivo = "arquivo_separado.csv"  # Nome do arquivo
    df = carregar_dados(caminho_arquivo)
    
    # Solicitar entrada do usuário para os filtros
    side = input("Digite o tipo de operação (BUY ou SELL): ").strip().upper()
    data_inicial = input("Digite a data inicial (YYYY-MM-DD): ").strip()
    data_final = input("Digite a data final (YYYY-MM-DD): ").strip()
    moeda_comprada = input("Digite a moeda vendida: ").strip().upper()
    moeda_vendida = input("Digite a moeda comprada: ").strip().upper()
    
    df_filtrado = filtrar_trades(df, side, data_inicial, data_final, moeda_comprada, moeda_vendida)
    
    total_gasto, total_recebido, custo_medio = calcular_totais(df_filtrado)
    
    print(f"Total gasto: {total_gasto:.2f}")
    print(f"Total recebido: {total_recebido:.2f}")
    print(f"Custo médio: {custo_medio:.2f}")
