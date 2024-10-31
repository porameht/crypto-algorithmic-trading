from rich.table import Table
from rich.console import Console
from rich.console import Console as RichConsole
from rich.text import Text
from rich.style import Style
from rich.theme import Theme
from datetime import datetime

class AccountInfoDisplayer:
    def __init__(self, session, title, timeframe, telegram=None, enable_logging=False):
        # Custom theme for rich console
        custom_theme = Theme({
            'info': Style(color='cyan', bold=True),
            'value': Style(color='magenta', bold=True), 
            'warning': Style(color='yellow', bold=True),
            'error': Style(color='red', bold=True),
            'success': Style(color='green', bold=True),
            'bold': Style(bold=True),
            'italic': Style(italic=True),
            'underline': Style(underline=True),
            'strike': Style(strike=True)
        })
        
        self.console = Console(theme=custom_theme)
        self.rich_console = RichConsole(record=True, theme=custom_theme)
        self.session = session
        self.title = title 
        self.timeframe = timeframe
        self.telegram = telegram
        self.enable_logging = enable_logging

    def display_account_info(self):        
        balance = self.session.get_balance()
        table = Table(
            show_header=True, 
            header_style="bold magenta",
            border_style="cyan",
            title=f"🚀 {self.title} Dashboard 🚀",
            title_style="bold cyan",
            box=None,
            padding=(0, 2)
        )
        
        table.add_column("📊 Metric", style="info")
        table.add_column("💫 Value", style="value")
        table.add_row("💰 Account Balance", f"<code>{balance} USDT</code>")
        table.add_row("⏱️ Timeframe", f"<code>{self.timeframe}</code>")
        
        try:
            positions = self.session.get_positions(200)
            last_pnl = self.session.get_last_pnl(100)
            current_pnl = self.session.get_current_pnl()
            net_profit = self.session.get_net_profit(last_hours=12)
            
            # Add rows with conditional styling based on values
            table.add_row("📂 Open Positions", f"<code>{len(positions)}</code>")
            
            pnl_style = "success" if float(last_pnl) >= 0 else "error"
            table.add_row("💰 Last 100 P&L", Text(f"<code>{last_pnl} USDT</code>", style=pnl_style))
            
            net_style = "success" if net_profit >= 0 else "error"
            table.add_row("🏖️ Net Profit (12Hr)", Text(f"<code>{round(net_profit, 3)} USDT</code>", style=net_style))
            
            current_style = "success" if float(current_pnl) >= 0 else "error"
            table.add_row("💹 Current P&L", Text(f"<code>{current_pnl} USDT</code>", style=current_style))
            
            # Display to console if logging enabled
            if self.enable_logging:
                self.console.print("\n")  # Add spacing
                self.console.print(table)
                self.console.print("\n")  # Add spacing
            
            # Send to Telegram if provided
            if self.telegram:
                telegram_message = self.format_telegram_message(
                    self.title, balance, self.timeframe, positions, 
                    last_pnl, current_pnl, net_profit
                )
                self.telegram.send_message(telegram_message)
            
            if positions:
                self.display_positions(positions, self.telegram)
                
        except Exception as err:
            error_msg = f"Error retrieving account info: {err}"
            self.console.print(f"[error]❌ {error_msg}[/error]")
            if self.telegram:
                self.telegram.send_message(f"❌ {error_msg}")
        return table

    def format_telegram_message(self, title, balance, timeframe, positions, 
                              last_pnl, current_pnl, net_profit):
        message = (
            f"<b>✨ Account Status ({title}) ✨</b>\n\n"
            f"<b>💰 Balance:</b> <code>{balance} USDT</code>\n"
            f"<b>⏱️ Timeframe:</b> <code>{timeframe}</code>\n"
            f"<b>📂 Open Positions:</b> <code>{len(positions)}</code>\n"
            f"<b>💰 Last 100 P&L:</b> <code>{last_pnl} USDT</code>\n"
            f"<b>🏖️ Net Profit (12Hr):</b> <code>{round(net_profit, 3)} USDT</code>\n"
            f"<b>💹 Current P&L:</b> <code>{current_pnl} USDT</code>\n"
            f"\n<i>🔸 Generated at: <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code></i>"
        )
        return message

    def display_positions(self, positions, telegram=None):
        pos_table = Table(
            show_header=True,
            header_style="bold cyan",
            title="📈 Active Trading Positions 📈",
            title_style="bold cyan",
            border_style="cyan",
            box=None,
            padding=(0, 1)
        )
        
        pos_table.add_column("Symbol", style="info")
        pos_table.add_column("Entry", style="value")
        pos_table.add_column("Side", style="value")
        pos_table.add_column("Size", style="value")
        pos_table.add_column("Take Profit", style="success")
        pos_table.add_column("Stop Loss", style="error")
        pos_table.add_column("TP %", style="success")
        pos_table.add_column("SL %", style="error")
        
        # Format positions for Telegram
        if telegram:
            positions_msg = "\n\n<b>✨ Open Positions ✨</b>\n"
            for elem in positions:
                tp_pct = self.calculate_percentage(elem['takeProfit'], elem['avgPrice'])
                sl_pct = self.calculate_percentage(elem['stopLoss'], elem['avgPrice'])
                
                side_emoji = "🟢" if elem['side'].upper() == "BUY" else "🔴"
                positions_msg += (
                    f"\n<b>{side_emoji} {elem['symbol']}</b>\n"
                    f"<b>💵 Entry:</b> <code>{elem['avgPrice']}</code>\n"
                    f"<b>📊 Side:</b> <code>{elem['side']}</code>\n"
                    f"<b>📏 Size:</b> <code>{elem['size']}</code>\n"
                    f"<b>🎯 Take Profit:</b> <code>{elem['takeProfit']} ({tp_pct})</code>\n"
                    f"<b>🛑 Stop Loss:</b> <code>{elem['stopLoss']} ({sl_pct})</code>\n"
                    f"<s>━━━━━━━━━━━━━━━</s>"
                )
            telegram.send_message(positions_msg)

        # Display in console if logging enabled
        if self.enable_logging:
            for elem in positions:
                tp_pct = self.calculate_percentage(elem['takeProfit'], elem['avgPrice'])
                sl_pct = self.calculate_percentage(elem['stopLoss'], elem['avgPrice'])
                
                side_style = "success" if elem['side'].upper() == "BUY" else "error"
                
                pos_table.add_row(
                    elem['symbol'],
                    str(elem['avgPrice']),
                    Text(elem['side'], style=side_style),
                    str(elem['size']),
                    str(elem['takeProfit']),
                    str(elem['stopLoss']),
                    tp_pct,
                    sl_pct
                )
            
            self.console.print("\n")  # Add spacing
            self.console.print(pos_table)
            self.console.print("\n")  # Add spacing

    def calculate_percentage(self, target_price, avg_price):
        if not target_price or not avg_price:
            return "N/A"
        percentage = ((float(target_price) - float(avg_price)) / float(avg_price)) * 100
        return f"{percentage:.2f}%"