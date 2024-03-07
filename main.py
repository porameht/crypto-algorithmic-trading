from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
# import bot_binance
import bot_bybit

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
