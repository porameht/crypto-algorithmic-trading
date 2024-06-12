import asyncio
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import uvicorn
from Bybit import Bybit
import bot_bybit
load_dotenv()


import os

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


@app.get("/")
async def read_root():
    api = os.getenv('API_BYBIT', None)
    secret = os.getenv('SECRET_BYBIT', None)
    accountType = os.getenv('ACCOUNT_TYPE', None)
    session = Bybit(api, secret, accountType)
    symbols = session.get_tickers()
    balance = session.get_balance()
    
    if balance is None or symbols is None:
        return { "error": "Can't connect" }
    
    try:
        positions = session.get_positions(200)
        last_pnl = session.get_last_pnl(100)
        current_pnl = session.get_current_pnl()
                
        return {
            "status": bot_status,
            "balance": balance,
            "positions": positions,
            "last_100_pnl": last_pnl,
            "current_pnl": current_pnl
        }
    
    except Exception as err:
        print(err)
        return { "error": "No connection" }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
