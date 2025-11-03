
from db import get_connection

def init_schema():
    with get_connection() as c:
        cur = c.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS customers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            contact TEXT
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS movies(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT,
            release_year INTEGER,
            rental_price REAL,
            producer TEXT,
            available INTEGER NOT NULL DEFAULT 1
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS rentals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            late_fee REAL DEFAULT 0
        )""")
        c.commit()

def seed_data():
    with get_connection() as c:
        cur = c.cursor()
        if cur.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0:
            cur.executemany("INSERT INTO employees(username,password) VALUES(?,?)",
                            [("admin","admin123"),("staff","staff123")])
        if cur.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
            cur.executemany("INSERT INTO customers(name,contact) VALUES(?,?)",
                            [("Alice Brown","alice@x.com"),
                             ("Brian Davis","brian@x.com"),
                             ("Chris Evans","chris@x.com"),
                             ("Dana Fox","dana@x.com")])
        if cur.execute("SELECT COUNT(*) FROM movies").fetchone()[0] == 0:
            cur.executemany("""INSERT INTO movies(title,genre,release_year,rental_price,producer,available)
                               VALUES(?,?,?,?,?,1)""",
                            [("Inception","Sci-Fi",2010,4.50,"Syncopy"),
                             ("The Matrix","Sci-Fi",1999,3.99,"Warner Bros"),
                             ("Interstellar","Sci-Fi",2014,4.99,"Paramount"),
                             ("Spirited Away","Animation",2001,3.49,"Studio Ghibli"),
                             ("Whiplash","Drama",2014,3.79,"Blumhouse"),
                             ("Parasite","Thriller",2019,4.49,"Barunson"),
                             ("Coco","Animation",2017,3.29,"Pixar")])
        c.commit()

def bootstrap():
    init_schema()
    seed_data()

if __name__ == "__main__":
    bootstrap()
