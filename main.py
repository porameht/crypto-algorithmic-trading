from fastapi import FastAPI
from dotenv import load_dotenv
import threading
from fastapi.responses import HTMLResponse
import uvicorn

load_dotenv()
import bot_bybit

app = FastAPI()

bot_status = "Not started"

def start():
    global bot_status
    bot_status = "Running"
    bot_bybit.run_bot()
    bot_status = "Stopped"

# @app.get("/status")
# async def status():
#     return {"status": bot_status}

@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
    <html>
        <head>
            <title>Trading Bot</title>
            <style>
                /* ...existing CSS... */
                body {{
                    background-color: #282c34;
                    color: white;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    width: 100%; /* full width */
                    height: 100%; /* full height */
                    font-family: Arial, sans-serif;
                    margin: 0; /* remove default margin */
                    padding: 0; /* remove default padding */
                    overflow: hidden; /* disable scrolling */
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

# ...existing threading code...
# def start():
#     bot_bybit.run_bot()

# use when uvicorn main:app --reload
bot_thread = threading.Thread(target=start)
bot_thread.daemon = True  # Set the thread as a daemon
bot_thread.start()

# use when python main.py
# if __name__ == "__main__":
#     bot_thread = threading.Thread(target=run_bot)
#     bot_thread.daemon = True  # Set the thread as a daemon
#     bot_thread.start()
#     uvicorn.run(app, host="0.0.0.0", port=8080)