from sentence_transformers import SentenceTransformer
import sqlite3
import numpy as np
import os

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")
#get path for the database file

model = SentenceTransformer("all-MiniLM-L6-v2") #set model type

connection = sqlite3.connect(path)




