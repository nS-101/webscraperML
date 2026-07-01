import sqlite3


try:
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS books(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL,
                   genre TEXT NOT NULL,
                   description TEXT, 
                   url TEXT UNIQUE NOT NULL
                   )
                   """)
    
 
    
    connection.commit()
    connection.close()
    
except sqlite3.Error as error:
    print(f"error is {error}")

