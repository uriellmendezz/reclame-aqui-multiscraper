import sqlite3
import os

def CreateDataBase():
    if not os.path.exists('database.db'):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Segments (
                id INTEGER NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Companies (
                id INTEGER NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                segment_id INTEGER,
                link TEXT,
                FOREIGN KEY(segment_id) REFERENCES Segments(id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Claims (
                id INTEGER NOT NULL PRIMARY KEY,
                id_company INTERGER,
                title TEXT,
                description TEXT,
                status TEXT,
                link TEXT
                       
                FOREIGN KEY(id_compnay) REFERENCES Companies (id)
            )''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Claims (
                id INTEGER NOT NULL PRIMARY KEY,
                id_company INTERGER,
                title TEXT,
                description TEXT,
                status TEXT,
                link TEXT
                       
                FOREIGN KEY(id_compnay) REFERENCES Companies (id)
            )''')
