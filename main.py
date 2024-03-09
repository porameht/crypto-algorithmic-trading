from fastapi import FastAPI
from dotenv import load_dotenv
import threading
import uvicorn

load_dotenv()
import bot_bybit

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

def run_bot():
    bot_bybit.run_bot()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    # bot_bybit.run_bot()

    uvicorn.run(app, host="0.0.0.0", port=8000)