from sentence_transformers import SentenceTransformer
import sqlite3
import numpy as np
import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")
#get path for the database file

model = SentenceTransformer("all-MiniLM-L6-v2") #set model type

connection = sqlite3.connect(path)
connection.row_factory = sqlite3.Row #access like dictionary instead of through indexes
cursor = connection.cursor()

cursor.execute("SELECT id, description FROM books") #get id and description from the database
booksData = cursor.fetchall() #store the ids and descriptions


validDescriptions = []
validBookIDs = []

for book in booksData:
    bookID = book["id"]
    description = book["description"]
    
    if description is None or description == "":
        continue
    
    validDescriptions.append(description)
    validBookIDs.append(bookID)

#above for loop separates valid books and invalid books

allEmbeddings = model.encode(validDescriptions, batch_size=32, show_progress_bar=True)
#batch processing for embedding since it's faster



for i in range(len(validBookIDs)):
    bookID = validBookIDs[i]
    bytesEmbedding = allEmbeddings[i].tobytes() #we can go by index since both arrays we created are of the same size
    
    cursor.execute("""
        INSERT INTO embeddings (bookID, embedding)
        VALUES (?, ?)
    """, (bookID, bytesEmbedding))
    
    print(bookID, validDescriptions[i][:20])

connection.commit()
connection.close()


