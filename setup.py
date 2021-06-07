import sqlite3
from passlib.hash import sha256_crypt as sha256

with sqlite3.connect('database.db') as connection:
            cursor = connection.cursor()
            cursor.execute('DROP TABLE IF EXISTS users')
            cursor.execute('CREATE TABLE users (username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, state TEXT, sessionID TEXT)')