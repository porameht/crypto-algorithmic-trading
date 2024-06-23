from rich.table import Table
from rich.console import Console

class AccountInfoDisplayer:
    def __init__(self):
        self.console = Console()

    def display_account_info(self, session, title, timeframe):
        balance = session.get_balance()
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column(f"Metric 👉{title} ", style="cyan")
        table.add_column("Value", style="magenta")
        table.add_row("💰 Account balance", f"{balance} USDT")
        table.add_row("⏱️  Timeframe ", f"{timeframe}")
        try:
            positions = session.get_positions(200)
            last_pnl = session.get_last_pnl(100)
            current_pnl = session.get_current_pnl()
            net_profit_12hr = session.get_net_profit(last_hours=12)
            
            # win_rate = session.get_win_rate()
            table.add_row("📂 Opened positions", f"{len(positions)}")
            table.add_row("💰 Last 100 P&L", f"{last_pnl} USDT")
            table.add_row("🏖️  Net profit 12Hr.", f"{round(net_profit_12hr, 3)} USDT")
            table.add_row("💹 Current P&L", f"{current_pnl} USDT")
            # table.add_row("🏆 Win Rate", f"{win_rate:.2f}%")
            self.console.print(table)
            
            if positions:
                self.display_positions(positions)
                
        except Exception as err:
            print(f"Error retrieving account info: {err}")
        return table

    def display_positions(self, positions):
        pos_table = Table(show_header=True, header_style="bold cyan")
        pos_table.add_column("📈 Symbol", style="cyan")
        pos_table.add_column("💵 Price", style="magenta")
        pos_table.add_column("📊 Side", style="magenta")
        pos_table.add_column("📏 Size", style="magenta")
        pos_table.add_column("🎯 TP", style="magenta")
        pos_table.add_column("🛑 SL", style="magenta")
        pos_table.add_column("📈 TP %", style="magenta")
        pos_table.add_column("📉 SL %", style="magenta")
        
        for elem in positions:
            take_profit_percentage = ((float(elem['takeProfit']) - float(elem['avgPrice'])) / float(elem['avgPrice'])) * 100 if elem['takeProfit'] else None
            stop_loss_percentage = ((float(elem['stopLoss']) - float(elem['avgPrice'])) / float(elem['avgPrice'])) * 100 if elem['stopLoss'] else None
            
            pos_table.add_row(
                elem['symbol'],
                str(elem['avgPrice']),
                elem['side'],
                str(elem['size']),
                str(elem['takeProfit']),
                str(elem['stopLoss']),
                f"{take_profit_percentage:.2f}%" if take_profit_percentage else "N/A",
                f"{stop_loss_percentage:.2f}%" if stop_loss_percentage else "N/A"
            )
            
        self.console.print(pos_table)