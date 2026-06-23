import sqlite3

db_path = r"C:\Users\Administrator\AppData\Roaming\pgadmin\pgadmin4.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print("Tables in pgAdmin database:", tables)
    
    if 'server' in tables:
        cursor.execute("SELECT id, name, host, port, username, password FROM server;")
        servers = cursor.fetchall()
        print(f"Found {len(servers)} server(s):")
        for s in servers:
            print(s)
            
except Exception as e:
    print("Error reading pgAdmin database:", e)
