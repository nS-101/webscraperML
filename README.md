# Book Discovery & Price Tracking Platform

A full-stack web application that scrapes book data, tracks price history over time, and uses NLP-powered semantic search to find books by meaning rather than keywords.

Built independently during the summer between first and second year at the University of Manchester as a portfolio project for second-year internship applications.

---

## What it does

- **Price Tracker** — scrapes 1000 books across 50 paginated pages, logs prices daily with timestamped entries, and displays an interactive price history graph per book
- **Semantic Search** — users describe what they want in plain English and the app returns the most conceptually similar books using sentence embeddings and cosine similarity
- **Recommendations** — each book detail page shows 5 "you might also like" suggestions, powered by the same embedding infrastructure as search
- **Genre Filtering** — homepage supports filtering all 1000 books by genre

---

## Tech Stack

| Layer | Tools |
|---|---|
| Scraping | Python, requests, BeautifulSoup4 |
| Database | SQLite3 |
| Web framework | Flask, Jinja2 |
| ML / NLP | SentenceTransformers, scikit-learn, NumPy |
| Frontend | HTML, CSS, Chart.js |
| Deployment | Railway |

---

## Architecture

The project follows a separation of concerns pattern — each file has one clear responsibility:

```
book-tracker/
├── WebScraper.py          # scrapes books.toscrape.com, calls database functions
├── database.py            # SQLite table creation, insertBook(), insertPrice()
├── generateEmbeddings.py  # one-time script: encodes descriptions, stores embeddings
├── app.py                 # Flask web app — three routes
├── database.db            # SQLite database (books, prices, embeddings tables)
└── templates/
    ├── base.html
    ├── index.html         # homepage with genre filter
    ├── book.html          # detail page — price graph + similar books
    └── search.html        # semantic search
```

---

## Database Design

Three tables with a clear separation of static and dynamic data:

**`books`** — one row per book, never duplicated. `url` has a `UNIQUE` constraint so `INSERT OR IGNORE` safely skips duplicates on subsequent scraper runs.

**`prices`** — a new row is inserted on every scraper run with a `DEFAULT CURRENT_TIMESTAMP`. This builds up timestamped price history rather than overwriting a single value, which is what enables the history graph.

**`embeddings`** — pre-computed sentence embeddings stored as binary BLOBs. Each embedding is a 384-dimensional numpy float32 array serialised with `.tobytes()` and reconstructed at read time with `np.frombuffer(bytes, dtype=np.float32)`.

---

## How the Semantic Search Works

**Pre-computation (runs once — `generateEmbeddings.py`):**
1. Fetch all 998 valid book descriptions from the database (2 books had no description and were skipped)
2. Batch encode with `model.encode(descriptions, batch_size=32)` using `all-MiniLM-L6-v2`
3. Serialise each 384-dimensional numpy array to bytes and store as a BLOB in the `embeddings` table

**At search time (`/search` route):**
1. Load and reconstruct all 998 stored embeddings from the database
2. Stack into a 2D matrix of shape `(998, 384)` with `np.stack()`
3. Encode the user's query — one embedding, near-instant
4. Compute `cosine_similarity([queryEmbedding], embeddingMatrix)` — returns 998 scores
5. Use `np.argsort(scores)[::-1][:5]` to get the indices of the top 5 matches
6. Map indices back to bookIDs and fetch book info from the database

Cosine similarity is used over Euclidean distance because it measures the angle between vectors rather than absolute distance — more reliable for capturing semantic alignment in high-dimensional space.

The SentenceTransformer model is loaded once at Flask startup rather than per request, since loading takes 2-3 seconds and would make every search unusable otherwise.

---

## Key Design Decisions

**Why pre-compute embeddings?**
Encoding 998 descriptions at query time would take 30-60 seconds per search. Pre-computing once and storing as BLOBs means only the user's query needs encoding at search time — the rest is matrix arithmetic.

**Why SQLite?**
File-based, zero-configuration, and built into Python. More than sufficient for a single-user application at this scale. In a production system with concurrent users I'd switch to PostgreSQL.

**Why simulate price fluctuations?**
`books.toscrape.com` is a static practice site — prices never change. A `random.uniform(-2.0, 2.0)` offset is added per scraper run to seed realistic history for the graph feature. This would be removed when pointing the scraper at a real bookshop.

**Why visit each book's detail page?**
Genre is not available on the homepage book cards — it lives in the breadcrumb navigation on each book's individual page. This requires one HTTP request per book but is the only reliable way to extract genre, which is critical for the ML dataset.

---

## Running Locally

```bash
# clone the repo
git clone https://github.com/nS-101/book-tracker.git
cd book-tracker

# install dependencies
pip install requests beautifulsoup4 flask sentence-transformers scikit-learn numpy

# set up the database
python3 database.py

# run the scraper (takes ~15 minutes for all 1000 books)
python3 WebScraper.py

# generate embeddings (run once)
python3 generateEmbeddings.py

# start the app
python3 app.py
# open http://127.0.0.1:5000
```

---

## What's Next

- Deploy on Railway for a live public URL
- Fine-tune a DistilBERT model for genre classification using the scraped descriptions as a training dataset
- Point the scraper at a real bookshop for genuine price history data
- Load embeddings into memory at startup rather than fetching from the database on every search request

---

## Skills Demonstrated

`web scraping` `relational database design` `REST APIs` `NLP` `sentence embeddings` `cosine similarity` `Flask` `SQLite` `data pipelines` `Python`
