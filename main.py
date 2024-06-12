import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import os

import uvicorn
import bot_bybit
from Bybit import Bybit
from tqdm import tqdm
from yaspin import yaspin
from rich import print
from rich.table import Table
from rich.console import Console
from time import sleep

from indicators.adjust_take_profit_stop_loss import adjust_take_profit_stop_loss
from indicators.combined_rsi_macd_signal import combined_rsi_macd_signal
from indicators.rsi_basic_signal import rsi_basic_signal

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_status
    bot_status = "Running"
    print('Bot is starting...')
    asyncio.create_task(bot_bybit.run_bot(bot_status))
    async with bot_context_manager():
        yield
    # Stop the bot here
    print('Bot is stopping...')
    bot_status = "Stopped"
    bot_bybit.run_bot(bot_status)
    

@asynccontextmanager
async def bot_context_manager():
    try:
        yield
    finally:
        print('Cleaning up bot context...')

app = FastAPI(lifespan=lifespan)

@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
    <html>
        <head>
            <title>Trading Bot</title>
            <style>
                body {{
                    background-color: #282c34;
                    color: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    width: 100%;
                    height: 100%;
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }}
                #status {{
                    color: {'#00ff00' if bot_status == 'Running' else '#ff0000'};
                }}
            </style>
        </head>
        <body>
            <h1>💨 Hi!, I'm Technical Trading Robot.</h1>
            <p>Designed and built with ❤️ by fr4nk.k, a dedicated Software Engineer@idindu research lab.</p>

            <p id="status">Current Status: {bot_status}</p>
            <p>Working tirelessly in the background, just for you. I'm currently using the following technical indicators for trading:</p>
            <ul>
                <li>RSI (Relative Strength Index)</li>
                <li>Stochastic RSI K</li>
                <li>Stochastic RSI D</li>
                <li>EMA (Exponential Moving Average) with a window of 200</li>
            </ul>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
