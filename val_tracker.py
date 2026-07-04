import sqlite3
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

DB_NAME = "valorant.db"
console = Console()

def setup_database():
    """Connects to SQLite and creates the matches table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT,
            map TEXT,
            result TEXT,
            rr_change INTEGER
        )
    ''')
    conn.commit()
    return conn

def log_match(conn):
    """Inserts a new match record into the database."""
    print("\n--- Log a New Match ---")
    agent = input("Agent played (e.g., Omen, Jett): ")
    map_name = input("Map (e.g., Ascent, Bind): ")
    result = input("Result (Win/Loss/Draw): ")
    rr = int(input("RR Change (e.g., 18, -14): "))
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO matches (agent, map, result, rr_change) 
        VALUES (?, ?, ?, ?)
    ''', (agent, map_name, result, rr))
    
    conn.commit()
    print("✅ Match logged successfully!\n")

def view_history(conn):
    """Queries and displays all logged matches in a table."""
    cursor = conn.cursor()
    cursor.execute('SELECT agent, map, result, rr_change FROM matches')
    matches = cursor.fetchall()
    
    table = Table(title="🎮 Match History", style="blue")
    table.add_column("Agent", style="cyan")
    table.add_column("Map", style="magenta")
    table.add_column("Result", justify="center")
    table.add_column("RR Change", justify="right")
    
    for match in matches:
        agent, map_name, result, rr = match
        result_str = f"[green]{result}[/green]" if result == "Win" else f"[red]{result}[/red]"
        rr_str = f"[green]+{rr}[/green]" if rr > 0 else f"[red]{rr}[/red]"
        table.add_row(agent, map_name, result_str, rr_str)
        
    console.print(table)
    print("\n")

def view_stats(conn):
    """Calculates and displays stats inside a formatted panel."""
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(rr_change) FROM matches')
    total_rr = cursor.fetchone()[0] or 0
    
    cursor.execute('SELECT COUNT(*) FROM matches WHERE result = "Win"')
    wins = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM matches')
    total_matches = cursor.fetchone()[0]
    
    if total_matches == 0:
        console.print(Panel("No matches logged yet.", title="Stats", style="yellow"))
        return
        
    win_rate = (wins / total_matches) * 100
    rr_display = f"[green]+{total_rr}[/green]" if total_rr > 0 else f"[red]{total_rr}[/red]"
    
    stats_text = (
        f"Total Matches Played: [bold]{total_matches}[/bold]\n"
        f"Overall Win Rate: [bold cyan]{win_rate:.1f}%[/bold cyan]\n"
        f"Net RR Change: [bold]{rr_display}[/bold]"
    )
    
    console.print(Panel(stats_text, title="📈 Performance Stats", expand=False, border_style="blue"))
    print("\n")

def main():
    conn = setup_database()
    
    while True:
        print("1. Log a match")
        print("2. View history")
        print("3. View overall stats")
        print("4. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            log_match(conn)
        elif choice == '2':
            view_history(conn)
        elif choice == '3':
            view_stats(conn)
        elif choice == '4':
            print("Exiting tracker...")
            conn.close()
            break

if __name__ == "__main__":
    main()
