import asyncio
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse
import uvicorn
from Bybit import Bybit
import bot_bybit
load_dotenv()
from prettytable import PrettyTable


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


def get_account_overview_table(balance, limit, positions, last_pnl, current_pnl) -> str:
    table = PrettyTable()
    table.field_names = ["Balance", "Positions", "Last PNL", "Current PNL"]
    
    # Populate the table with your data
    table.add_row([balance, positions, last_pnl, current_pnl])
    
    return table.get_html_string()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    api = os.getenv('API_BYBIT', None)
    secret = os.getenv('SECRET_BYBIT', None)
    accountType = os.getenv('ACCOUNT_TYPE', None)
    session = Bybit(api, secret, accountType)
    symbols = session.get_tickers()
    balance = session.get_balance()
    
    if balance is None or symbols is None:
        return HTMLResponse(content="<p>❌ Can't connect</p>", status_code=500)
    
    try:
        positions = session.get_positions(200)
        last_pnl = session.get_last_pnl(100)
        current_pnl = session.get_current_pnl()
        
        table_html = get_account_overview_table(balance, 30, positions, last_pnl, current_pnl)
        
        return HTMLResponse(content=table_html, status_code=200)
    
    except Exception as err:
        print(err)
        return HTMLResponse(content="<p>No connection</p>", status_code=500)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
