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

# --- Input Validation Helpers ---
def get_valid_string(prompt):
    """Ensures input isn't empty and title-cases it to normalize stats."""
    while True:
        value = input(prompt).strip()
        if value:
            return value.title()
        print("⚠️ Input cannot be empty. Please try again.")

def get_valid_result(prompt):
    """Restricts result input to exactly Win, Loss, or Draw."""
    valid_results = {"Win", "Loss", "Draw"}
    while True:
        value = input(prompt).strip().title()
        if value in valid_results:
            return value
        print("⚠️ Invalid result. Please enter Win, Loss, or Draw.")

def get_valid_int(prompt):
    """Catches ValueErrors if the user types letters instead of numbers."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("⚠️ Invalid input. Please enter a whole number.")

def log_match(conn):
    """Inserts a new match record into the database."""
    print("\n--- Log a New Match ---")
    agent = get_valid_string("Agent played (e.g., Omen, Jett): ")
    map_name = get_valid_string("Map (e.g., Ascent, Bind): ")
    result = get_valid_result("Result (Win/Loss/Draw): ")
    rr = get_valid_int("RR Change (e.g., 18, -14, or 0 for Draw): ")
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO matches (agent, map, result, rr_change) 
        VALUES (?, ?, ?, ?)
    ''', (agent, map_name, result, rr))
    
    conn.commit()
    print("✅ Match logged successfully!\n")

def delete_last_match(conn):
    """Removes the most recently added match to fix fat-finger mistakes."""
    cursor = conn.cursor()
    cursor.execute('SELECT id, agent, map, result FROM matches ORDER BY id DESC LIMIT 1')
    match = cursor.fetchone()
    
    if not match:
        print("⚠️ No matches in the database to delete.\n")
        return
        
    match_id, agent, map_name, result = match
    print(f"\nLast logged match: {agent} on {map_name} ({result})")
    
    confirm = get_valid_string("Are you sure you want to delete this match? (Y/N): ")
    if confirm.startswith('Y'):
        cursor.execute('DELETE FROM matches WHERE id = ?', (match_id,))
        conn.commit()
        print("🗑️ Match deleted successfully!\n")
    else:
        print("❌ Deletion cancelled.\n")

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
        
        # Explicit 3-way color logic for results
        if result == "Win":
            result_str = "[green]Win[/green]"
        elif result == "Loss":
            result_str = "[red]Loss[/red]"
        else:
            result_str = "[yellow]Draw[/yellow]"
            
        # Color code RR logic
        if rr > 0:
            rr_str = f"[green]+{rr}[/green]"
        elif rr < 0:
            rr_str = f"[red]{rr}[/red]"
        else:
            rr_str = "[yellow]0[/yellow]"
            
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
    
    if total_rr > 0:
        rr_display = f"[green]+{total_rr}[/green]"
    elif total_rr < 0:
        rr_display = f"[red]{total_rr}[/red]"
    else:
        rr_display = "[yellow]0[/yellow]"
    
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
        print("4. Delete last match (Undo)")
        print("5. Exit")
        
        choice = input("Select an option: ").strip()
        
        if choice == '1':
            log_match(conn)
        elif choice == '2':
            view_history(conn)
        elif choice == '3':
            view_stats(conn)
        elif choice == '4':
            delete_last_match(conn)
        elif choice == '5':
            print("Exiting tracker...")
            conn.close()
            break
        else:
            print("⚠️ Invalid choice. Please enter 1, 2, 3, 4, or 5.\n")

if __name__ == "__main__":
    main()
