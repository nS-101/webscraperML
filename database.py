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
    
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS prices(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   bookID INTEGER NOT NULL,
                   price REAL NOT NULL,
                   availability TEXT NOT NULL,
                   scrapedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                   FOREIGN KEY (bookID) REFERENCES books(id)
                   )
                   """)
    
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   bookID INTEGER NOT NULL,
                   embedding BLOB NOT NULL,
                   FOREIGN KEY (bookID) REFERENCES books(id)
                   )
                   """)
    
    #using BLOB data type to store embeddings because it's the most
    #pragmatic way to store 768 numbers to represent the embeddings
    connection.commit()
    connection.close()
    
except sqlite3.Error as error:
    print(f"error is {error}")

def insertBook(title, genre, description, url):
    try:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("""
                       INSERT OR IGNORE INTO books (title, genre, description, url)
            VALUES (?, ?, ?, ?)
                       """, (title, genre, description, url))

        connection.commit()

        cursor.execute("SELECT id FROM books WHERE url = ?", (url,))
        bookID = cursor.fetchone()[0] #get the book id
        connection.close()
        return bookID

    except sqlite3.Error as error:
        print(f"there is an error {error}")

def insertPrice(bookID, price, availability):
    try: 
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(""" 
                           INSERT INTO prices (bookID, price, availability)
                       VALUES(?, ?, ?)
                        """, (bookID, price, availability))
        connection.commit()
        connection.close()
    
    except sqlite3.Error as error:
        print(f"error is {error}")