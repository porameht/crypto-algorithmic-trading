# Trading Bot with Bybit Integration

This project implements a trading bot that interacts with the Bybit API to execute trades based on predefined signals. The bot supports running multiple instances concurrently, each with its own configuration, trading strategy, and account information display.

## Project Structure

- `config.py`: Handles loading environment variables and configuration settings.
- `trading_bot.py`: Contains the `TradingBotBybit` class which manages the trading logic, account information display, and execution of trades.
- `main.py`: The entry point of the application, initializing bot instances and running them concurrently.
- `AccountInfoDisplayer.py`: Contains the class for displaying account information in a structured format.
- `Bybit.py`: Contains the class for interacting with the Bybit API.
- `indicators/`: Directory containing signal functions used by the trading bot.

## Features

- **Multi-Session Support**: Run multiple trading bot instances with different configurations.
- **Signal-Based Trading**: Execute trades based on custom signal functions (e.g., combined RSI and MACD, Jim Simons signal).
- **Account Information Display**: Display account balance, open positions, and P&L in a structured table format using the `rich` library.
- **Concurrent Execution**: Utilize Python's `ThreadPoolExecutor` for concurrent execution of multiple bot instances.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/porameht/trading-bot.git
   cd trading-bot-bybit
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory and add your Bybit API credentials and other configuration settings:
   ```env
   API_BYBIT=your_main_account_api_key
   SECRET_BYBIT=your_main_account_secret_key
   ACCOUNT_TYPE=main_account_type
   API_BYBIT_WORKER1=your_worker1_account_api_key
   SECRET_BYBIT_WORKER1=your_worker1_account_secret_key
   ACCOUNT_TYPE_WORKER1=worker1_account_type
   ```

## Usage

1. **Configure the trading bot**:
   Edit the `session_configs` in `main.py` to customize the settings for each bot instance, including API keys, account types, trading strategies, and display titles.

2. **Run the bot**:
   ```bash
   python main.py
   ```

## Example

```python
# main.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import load_config
from TradingBotBybit import TradingBotBybit
from indicators.combined_rsi_macd_signal import combined_rsi_macd_signal
from indicators.jim_simons import jim_simons_signal

def main():
    config = load_config()

    session_configs = [
        {
            'api': config['api_main'],
            'secret': config['secret_main'],
            'accountType': config['accountType_main'],
            'mode': config['mode'],
            'leverage': config['leverage'],
            'timeframe': config['timeframe'],
            'qty': config['qty'],
            'max_positions': config['max_positions'],
            'signal_func': jim_simons_signal,
            'title': "📊 Account Information Main"
        },
        {
            'api': config['api_worker1'],
            'secret': config['secret_worker1'],
            'accountType': config['accountType_worker1'],
            'mode': config['mode'],
            'leverage': config['leverage'],
            'timeframe': config['timeframe'],
            'qty': config['qty'],
            'max_positions': config['max_positions'],
            'signal_func': combined_rsi_macd_signal,
            'title': "📊 Account Information Worker1"
        }
    ]

    bots = [TradingBotBybit(session_config) for session_config in session_configs]

    with ThreadPoolExecutor(max_workers=len(bots)) as executor:
        futures = [executor.submit(bot.run) for bot in bots]
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as err:
                print(f"Error in bot execution: {err}")

if __name__ == "__main__":
    main()
```

## Customization

- **Signal Functions**: Implement your own signal functions in the `indicators` directory and update the `session_configs` in `main.py` to use them.
- **Bot Settings**: Adjust the bot settings (mode, leverage, timeframe, etc.) in the `session_configs` to suit your trading preferences.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributions

Contributions are welcome! Please submit a pull request or open an issue to discuss any changes.

## Contact

For any questions or support, please open an issue or contact the project maintainer.
