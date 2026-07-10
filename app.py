import sqlite3
import json
import os
from flask import Flask, render_template, request, abort
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity #needed to compare two different embeddings(user and everything else in database)
import numpy as np

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

model = SentenceTransformer("all-MiniLM-L6-v2")

def getDb():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    selectedGenre = request.args.get("genre", "")
    conn = getDb()

    genres = [
        row[0]
        for row in conn.execute(
            "SELECT DISTINCT genre FROM books ORDER BY genre"
        ).fetchall()
    ]

    if selectedGenre:
        books = conn.execute(
            """
            SELECT b.id, b.title, b.genre, p.price, p.availability
            FROM books b
            JOIN prices p ON b.id = p.bookID
            WHERE p.id = (SELECT MAX(id) FROM prices WHERE bookID = b.id)
              AND b.genre = ?
            ORDER BY b.title
            """,
            (selectedGenre,),
        ).fetchall()
    else:
        books = conn.execute(
            """
            SELECT b.id, b.title, b.genre, p.price, p.availability
            FROM books b
            JOIN prices p ON b.id = p.bookID
            WHERE p.id = (SELECT MAX(id) FROM prices WHERE bookID = b.id)
            ORDER BY b.title
            """
        ).fetchall()

    conn.close()
    return render_template("index.html", books=books, genres=genres, selectedGenre=selectedGenre)


@app.route("/book/<int:bookId>")
def bookDetail(bookId):
    conn = getDb()

    book = conn.execute("SELECT * FROM books WHERE id = ?", (bookId,)).fetchone()
    if not book:
        abort(404)

    priceHistory = conn.execute(
        "SELECT price, scrapedAt FROM prices WHERE bookID = ? ORDER BY scrapedAt",
        (bookId,),
    ).fetchall()

    conn.close()

    labels = [row["scrapedAt"] for row in priceHistory]
    prices = [row["price"] for row in priceHistory]

    return render_template(
        "book.html",
        book=book,
        labels=json.dumps(labels),
        prices=json.dumps(prices),
    )


@app.route("/search")
def search():
    query = request.args.get("q", "")
    results = []
    connection = getDb() #establish connection to the database
    cursor = connection.cursor()

    cursor.execute("""
                SELECT bookID, embedding FROM embeddings
                   """)
    everything = cursor.fetchall()
    bookIDsFromTable = [row[0] for row in everything] #create list of just ids
    embeddingsOfBooksFromTable = [row[1] for row in everything] #create list of embeddings

    deconstructedBookIDs = []
    deconstructedEmbeddings = []
    for i in range(len(embeddingsOfBooksFromTable)):
        deconstructedBookIDs.append(bookIDsFromTable[i]) #add id to list
        decodedEmbedding = np.frombuffer(embeddingsOfBooksFromTable[i], dtype=np.float32) #convert from BLOB to array of floats(deconversion)
        deconstructedEmbeddings.append(decodedEmbedding) #add decoded embedding to the list


    if query:
        encodedQuery = model.encode(query) #create embedding
        encodedQuery = [encodedQuery] #turn into 2d array for cosine_similarity method
        
        collapsedArray = np.stack(deconstructedEmbeddings, axis=0) #arrays are stored horizontally
        similarityScores = cosine_similarity(encodedQuery, collapsedArray) #run the cosine method to compare user embedding to the other embeddings
        similarityScores = similarityScores[0] #get similarity scores for the user search

        similarityScores = np.argsort(similarityScores)[::-1] #sort indexes by highest similarity to the lowest
        topFiveSimilarity = similarityScores[:5] #get five highest similarity scores

        topFiveBookIDs = []
        for index in topFiveSimilarity:
            topFiveBookIDs.append(deconstructedBookIDs[index]) #create list of top five bookids corresponding to the top five similarity scores


        for id in topFiveBookIDs:
            cursor.execute("""
                           SELECT b.id, b.title, b.genre, p.price
                            FROM books b
                            JOIN prices p ON b.id = p.bookID
                            WHERE b.id = ?
                            AND p.id = (SELECT MAX(id) FROM prices WHERE bookID = b.id)
                           """,(id,))
            currentResults =  cursor.fetchone()
            results.append({
                "id": currentResults["id"],
                "title": currentResults["title"],
                "genre": currentResults["genre"],
                "price": currentResults["price"] 
            })
    connection.close()
    return render_template("search.html", query=query, results=results)
    #does this run every time that a user searches???????
    #yes it does, could be a performance issue if we scale up

if __name__ == "__main__":
    app.run(debug=True)
