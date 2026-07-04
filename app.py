import sqlite3
import json
import os
from flask import Flask, render_template, request, abort
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")


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
    return render_template("search.html", query=query)


if __name__ == "__main__":
    app.run(debug=True)
