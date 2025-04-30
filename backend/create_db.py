import sqlite3

def create_db():
    conn = sqlite3.connect('alerts.db')
    cursor = conn.cursor()

    # Create the alerts table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        ip TEXT,
        type TEXT,
        attempts INTEGER,
        status TEXT
    )''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
    print("✅ Database created.")
