import asyncio
from Bybit import Bybit
from time import sleep
import os
from tqdm import tqdm
# from yaspin import yaspin
from rich import print
from rich.table import Table
from rich.console import Console

from indicators.adjust_take_profit_stop_loss import adjust_take_profit_stop_loss
from indicators.combined_rsi_macd_signal import combined_rsi_macd_signal
from indicators.rsi_basic_signal import rsi_basic_signal

api = os.getenv('API_BYBIT', None)
secret = os.getenv('SECRET_BYBIT', None)
accountType = os.getenv('ACCOUNT_TYPE', None)

session = Bybit(api, secret, accountType)

mode = 1  # 1 - Isolated, 0 - Cross
leverage = 10  # 10x
timeframe = 30 # 15 minutes
qty = 10 # Amount of USDT for one order
max_positions = 10 # max 10 positions

symbols = session.get_tickers()

console = Console()

async def run_bot(bot_status):
    while bot_status == "Running":
        balance = session.get_balance()
        if balance is None or symbols is None:
            print('❌ Cant connect')
            await asyncio.sleep(120)
            continue

        # Create a table for account balance and P&L
        table = Table(title="Account Overview")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")

        table.add_row("💰 Account balance", f"{balance} USDT")
        table.add_row("⏱️  Timeframe", f"{timeframe} minutes")

        try:
            positions = session.get_positions(200)
            last_pnl = session.get_last_pnl(100)
            current_pnl = session.get_current_pnl()
            
            table.add_row("📂 Opened positions", f"{len(positions)}")
            table.add_row("💰 Last 100 P&L", f"{last_pnl} USDT")
            table.add_row("💹 Current P&L", f"{current_pnl} USDT")

            console.print(table)

            for i, elem in enumerate(symbols, start=1):
                if len(positions) >= max_positions:
                    break
                signal, kl = combined_rsi_macd_signal(session, elem, timeframe)
                    
                if signal == 'up' and not elem in positions:
                    tp, sl = adjust_take_profit_stop_loss(kl)
                    session.place_order_market(elem, 'buy', mode, leverage, qty, tp, sl)
                    await asyncio.sleep(1)
                if signal == 'down' and not elem in positions:
                    tp, sl = adjust_take_profit_stop_loss(kl)
                    session.place_order_market(elem, 'sell', mode, leverage, qty, tp, sl)
                    await asyncio.sleep(1)

        except Exception as err:
            print(err)
            print('No connection')
            for i in tqdm(range(60, 0, -1)):
                await asyncio.sleep(1)

        for i in tqdm(range(100, 0, -5)):
            await asyncio.sleep(1)
