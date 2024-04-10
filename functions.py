from concurrent.futures import ThreadPoolExecutor
import os, random, time, datetime, sqlite3, pandas as pd

def connect_database(database_name="database.db"):
    if not os.path.exists('database.db'):
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Segments (
                id INTEGER NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                link TEXT
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Companies (
                id INTEGER NOT NULL PRIMARY KEY,
                name TEXT,
                shortName TEXT,
                IdSegment INTEGER,
                link TEXT,
                FOREIGN KEY(IdSegment) REFERENCES Segments(id)
            )''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Claims (
                id INTEGER NOT NULL PRIMARY KEY,
                IdCompany INTERGER,
                title TEXT,
                description TEXT,
                status TEXT,
                link TEXT,  
                FOREIGN KEY(IdCompany) REFERENCES Companies (id)
            )''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CompaniesIds (
                id TEXT UNIQUE NOT NULL PRIMARY KEY,
                shortName TEXT
            )''')

        connection.commit()
        return connection
    else:
        connection = sqlite3.connect("database.db")
        return connection

def calculate_process_duration(start, end):
    total = end - start
    formatted = datetime.timedelta(seconds=total)
    return  str(formatted)


def random_sleep_time(min, max):
    if max <= min:
        raise ValueError('max must be greater than min')
    
    sleep_time = random.uniform(max, min)
    time.sleep(sleep_time)

