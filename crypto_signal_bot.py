import requests
import pandas as pd
import time
import telegram
import asyncio

# --- CONFIG ---
TELEGRAM_TOKEN = '8158169533:AAHZPkDUuYWAkYDhH2nNiegGZT06QTOdin4'  # <-- Thay bằng Token bạn vừa lấy
TELEGRAM_CHAT_ID = '5694180372'  # <-- Lấy Chat ID (mình hướng dẫn bên dưới)

# Sàn bạn muốn lấy giá
EXCHANGES = ['binance', 'okx']

# Memecoins cố định
MEMECOINS = ['DOGEUSDT', 'SHIBUSDT', 'PEPEUSDT', 'FLOKIUSDT', 'WIFUSDT', 'BONKUSDT', 'MEMEUSDT']

# Điều kiện lọc
PERCENT_CHANGE_THRESHOLD = 2.0  # 2%

# API endpoint mẫu
API_BINANCE = 'https://api.binance.com/api/v3/klines'
API_OKX = 'https://www.okx.com/api/v5/market/candles'

# Khởi tạo bot telegram
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# --- FUNCTION ---

def get_binance_klines(symbol):
    try:
        url = f"{API_BINANCE}?symbol={symbol}&interval=4h&limit=55"
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', '_', '__', '___', '____', '_____'])
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        print(f"Error Binance {symbol}: {e}")
        return None

def get_okx_klines(symbol):
    try:
        okx_symbol = symbol.replace('USDT', '-USDT')
        url = f"{API_OKX}?instId={okx_symbol}&bar=4H&limit=55"
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', '_'])
        df['close'] = df['close'].astype(float)
        return df
    except Exception as e:
        print(f"Error OKX {symbol}: {e}")
        return None

def calculate_ema(df, period):
    return df['close'].ewm(span=period, adjust=False).mean()

async def main_loop():
    while True:
        for exchange in EXCHANGES:
            if exchange == 'binance':
                coins = MEMECOINS + get_binance_top_movers()
                for symbol in coins:
                    df = get_binance_klines(symbol)
                    if df is not None:
                        await check_and_send_signal(symbol, df, exchange)
            elif exchange == 'okx':
                coins = MEMECOINS + get_okx_top_movers()
                for symbol in coins:
                    df = get_okx_klines(symbol)
                    if df is not None:
                        await check_and_send_signal(symbol, df, exchange)
        await asyncio.sleep(4 * 60 * 60)  # 4 giờ

async def check_and_send_signal(symbol, df, exchange):
    df['ema50'] = calculate_ema(df, 50)
    df['ema200'] = calculate_ema(df, 200)

    current_close = df.iloc[-1]['close']
    percent_change = ((df.iloc[-1]['close'] - df.iloc[-2]['close']) / df.iloc[-2]['close']) * 100

    if abs(percent_change) >= PERCENT_CHANGE_THRESHOLD or symbol in MEMECOINS:
        signal = "BUY 📈" if df.iloc[-1]['ema50'] > df.iloc[-1]['ema200'] else "SELL 📉"
        msg = (
            f"🔥 [{exchange.upper()}] {symbol}\n"
            f"Price: ${current_close:.2f}\n"
            f"Change (4H): {percent_change:.2f}%\n"
            f"Signal: {signal}\n"
        )
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

def get_binance_top_movers():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    data = response.json()
    movers = [d['symbol'] for d in data if abs(float(d['priceChangePercent'])) >= PERCENT_CHANGE_THRESHOLD and d['symbol'].endswith('USDT')]
    return movers

def get_okx_top_movers():
    url = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
    response = requests.get(url)
    data = response.json()
    movers = [d['instId'].replace('-USDT', 'USDT') for d in data['data'] if abs(float(d['change24h'])) >= PERCENT_CHANGE_THRESHOLD and d['instId'].endswith('-USDT')]
    return movers

# --- RUN BOT ---
if __name__ == '__main__':
    asyncio.run(main_loop())
