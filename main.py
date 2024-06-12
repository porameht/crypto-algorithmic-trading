import asyncio
from fastapi import FastAPI
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import uvicorn
import bot_bybit
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

@app.get("/")
async def read_root():
    return { "bot_status": bot_status }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
