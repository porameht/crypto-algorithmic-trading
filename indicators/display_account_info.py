from rich.table import Table
from rich.console import Console

console = Console()

def display_account_info(session, title, timeframe):
    balance = session.get_balance()
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("💰 Account balance", f"{balance} USDT")
    table.add_row("⏱️  Timeframe ", f"{timeframe} minutes")
    try:
        positions = session.get_positions(200)
        last_pnl = session.get_last_pnl(100)
        current_pnl = session.get_current_pnl()
        table.add_row("📂 Opened positions", f"{len(positions)}")
        table.add_row("💰 Last 100 P&L", f"{last_pnl} USDT")
        table.add_row("💹 Current P&L", f"{current_pnl} USDT")
        
        if positions:
            pos_table = Table(title="📊 Open Positions", show_header=True, header_style="bold cyan")
            pos_table.add_column("📈 Symbol", style="cyan")
            pos_table.add_column("💵 Avg Price", style="magenta")
            pos_table.add_column("📊 Side", style="magenta")
            pos_table.add_column("📏 Size", style="magenta")
            pos_table.add_column("📉 Entry Price", style="magenta")
            pos_table.add_column("🎯 Take Profit", style="magenta")
            pos_table.add_column("🛑 Stop Loss", style="magenta")
            
            for elem in positions:
                pos_table.add_row(
                    elem['symbol'],
                    str(elem['avgPrice']),
                    elem['side'],
                    str(elem['size']),
                    str(elem['entryPrice']),
                    str(elem['takeProfit']),
                    str(elem['stopLoss'])
                )
            console.print(pos_table)
            
    except Exception as err:
        print(f"Error retrieving account info: {err}")
    return table