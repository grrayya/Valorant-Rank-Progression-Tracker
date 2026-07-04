import sqlite3

DB_NAME = "valorant.db"

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
    """Queries and displays all logged matches."""
    cursor = conn.cursor()
    cursor.execute('SELECT agent, map, result, rr_change FROM matches')
    matches = cursor.fetchall()
    
    print("\n--- Match History ---")
    if not matches:
        print("No matches logged yet.")
    else:
        for match in matches:
            print(f"🎮 {match[0]} on {match[1]} | {match[2]} ({match[3]} RR)")
    print("---------------------\n")
    
def view_stats(conn):
    """Calculates win rate and net RR using SQL aggregations."""
    cursor = conn.cursor()
    
    # Get Total RR
    cursor.execute('SELECT SUM(rr_change) FROM matches')
    total_rr = cursor.fetchone()[0] or 0
    
    # Get Win/Loss counts
    cursor.execute('SELECT COUNT(*) FROM matches WHERE result = "Win"')
    wins = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM matches')
    total_matches = cursor.fetchone()[0]
    
    print("\n--- 📈 Performance Stats ---")
    print(f"Total Matches Played: {total_matches}")
    
    if total_matches > 0:
        win_rate = (wins / total_matches) * 100
        print(f"Overall Win Rate: {win_rate:.1f}%")
        
        # Color code the RR based on positive or negative
        rr_display = f"+{total_rr}" if total_rr > 0 else str(total_rr)
        print(f"Net RR Change: {rr_display}")
    print("----------------------------\n")
    
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
            break

if __name__ == "__main__":
    main()
