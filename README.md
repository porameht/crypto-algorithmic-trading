# Crypto Trading Bot

A robust cryptocurrency trading bot built with Python, implementing multiple trading strategies and real-time notifications.

## Features

- Multiple trading strategies (RSI, MACD, Jim Simons)
- Real-time Telegram notifications
- Risk management
- Account information tracking
- Bybit exchange integration
- Concurrent strategy execution
- Configurable parameters

## Setup

1. Clone the repository:
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

5. **Configure the trading bot**:
   Edit the `session_configs` in `main.py` to customize the settings for each bot instance, including API keys, account types, trading strategies, and display titles.

6. **Run the bot**:
   ```bash
   python main.py
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
