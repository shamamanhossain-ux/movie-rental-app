# models.py — consistent with app.py/movie_view.py/customer_view.py/rental_view.py

from datetime import datetime
from db import get_connection

DATE_FMT = "%Y-%m-%d"
LATE_FEE_PER_DAY = 2.0


# -------------------- AUTH --------------------
def check_login(username, password):
    with get_connection() as c:
        row = c.execute(
            "SELECT id FROM employees WHERE username=? AND password=?",
            (username, password),
        ).fetchone()
        return row is not None


# -------------------- CUSTOMERS --------------------
def customers_list(q_name=None, q_id=None):
    sql = "SELECT id,name,contact FROM customers WHERE 1=1"
    args = []
    if q_name:
        sql += " AND name LIKE ?"
        args.append(f"%{q_name}%")
    if q_id:
        sql += " AND id = ?"
        args.append(q_id)
    sql += " ORDER BY id DESC"
    with get_connection() as c:
        return c.execute(sql, args).fetchall()


def customer_add(name, contact):
    with get_connection() as c:
        c.execute("INSERT INTO customers(name,contact) VALUES(?,?)", (name, contact))
        c.commit()


def customer_update(cust_id, name, contact):
    with get_connection() as c:
        c.execute(
            "UPDATE customers SET name=?, contact=? WHERE id=?",
            (name, contact, cust_id),
        )
        c.commit()


def customer_delete(cust_id):
    with get_connection() as c:
        has = c.execute(
            "SELECT 1 FROM rentals WHERE customer_id=? AND return_date IS NULL",
            (cust_id,),
        ).fetchone()
        if has:
            raise ValueError("Cannot delete – active rentals exist.")
        c.execute("DELETE FROM customers WHERE id=?", (cust_id,))
        c.commit()


# -------------------- MOVIES --------------------
def movies_list(title=None, genre=None, producer=None, year=None, price_min=None, price_max=None):
    sql = (
        "SELECT id,title,genre,release_year,rental_price,producer,available "
        "FROM movies WHERE 1=1"
    )
    args = []
    if title:
        sql += " AND title LIKE ?"
        args.append(f"%{title}%")
    if genre:
        sql += " AND genre LIKE ?"
        args.append(f"%{genre}%")
    if producer:
        sql += " AND producer LIKE ?"
        args.append(f"%{producer}%")
    if year:
        sql += " AND release_year = ?"
        args.append(year)
    if price_min is not None:
        sql += " AND rental_price >= ?"
        args.append(price_min)
    if price_max is not None:
        sql += " AND rental_price <= ?"
        args.append(price_max)
    sql += " ORDER BY id DESC"
    with get_connection() as c:
        return c.execute(sql, args).fetchall()


def available_movies():
    with get_connection() as c:
        return c.execute(
            "SELECT id,title FROM movies WHERE available=1 ORDER BY title"
        ).fetchall()


def movie_add(title, genre, year, price, producer):
    with get_connection() as c:
        c.execute(
            """
            INSERT INTO movies(title,genre,release_year,rental_price,producer,available)
            VALUES(?,?,?,?,?,1)
            """,
            (title, genre, year, price, producer),
        )
        c.commit()


def movie_update(mid, title, genre, year, price, producer):
    with get_connection() as c:
        c.execute(
            """
            UPDATE movies
               SET title=?, genre=?, release_year=?, rental_price=?, producer=?
             WHERE id=?
            """,
            (title, genre, year, price, producer, mid),
        )
        c.commit()


def movie_delete(mid):
    with get_connection() as c:
        has = c.execute(
            "SELECT 1 FROM rentals WHERE movie_id=? AND return_date IS NULL", (mid,)
        ).fetchone()
        if has:
            raise ValueError("Cannot delete – movie is currently rented.")
        c.execute("DELETE FROM movies WHERE id=?", (mid,))
        c.commit()


# -------------------- RENTALS --------------------
def rentals_list(customer=None, movie=None, issue=None, ret=None):
    sql = """
        SELECT r.id, c.name AS customer, m.title AS movie, r.issue_date, r.due_date,
               r.return_date, r.late_fee
          FROM rentals r
          JOIN customers c ON c.id = r.customer_id
          JOIN movies    m ON m.id = r.movie_id
         WHERE 1=1
    """
    args = []
    if customer:
        sql += " AND c.name LIKE ?"
        args.append(f"%{customer}%")
    if movie:
        sql += " AND m.title LIKE ?"
        args.append(f"%{movie}%")
    if issue:
        sql += " AND r.issue_date = ?"
        args.append(issue)
    if ret is not None and ret != "":
        # empty string means "only non-returned" if caller passes ""
        sql += " AND IFNULL(r.return_date,'') = ?"
        args.append(ret)
    sql += " ORDER BY r.id DESC"
    with get_connection() as c:
        return c.execute(sql, args).fetchall()


def issue_movie(customer_id, movie_id, issue_date, due_date):
    with get_connection() as c:
        cur = c.cursor()
        ok = cur.execute("SELECT available FROM movies WHERE id=?", (movie_id,)).fetchone()
        if not ok or ok[0] != 1:
            raise ValueError("Movie not available.")
        cur.execute(
            "INSERT INTO rentals(customer_id,movie_id,issue_date,due_date) VALUES(?,?,?,?)",
            (customer_id, movie_id, issue_date, due_date),
        )
        cur.execute("UPDATE movies SET available=1-1 WHERE id=?", (movie_id,))  # set to 0
        c.commit()


def return_movie(rental_id, return_date):
    with get_connection() as c:
        cur = c.cursor()
        r = cur.execute(
            "SELECT movie_id,due_date FROM rentals WHERE id=?", (rental_id,)
        ).fetchone()
        if not r:
            raise ValueError("Rental not found.")
        movie_id, due_text = r[0], r[1]
        due = datetime.strptime(due_text, DATE_FMT).date()
        ret_d = datetime.strptime(return_date, DATE_FMT).date()
        late_days = max(0, (ret_d - due).days)
        fee = float(late_days) * LATE_FEE_PER_DAY
        cur.execute(
            "UPDATE rentals SET return_date=?, late_fee=? WHERE id=?",
            (return_date, fee, rental_id),
        )
        cur.execute("UPDATE movies SET available=1 WHERE id=?", (movie_id,))
        c.commit()
        return fee


# -------------------- STATS (for charts) --------------------
def stats_rentals_per_genre():
    with get_connection() as c:
        return c.execute(
            """
            SELECT m.genre AS label, COUNT(*) AS cnt
              FROM rentals r JOIN movies m ON m.id=r.movie_id
             GROUP BY m.genre
             ORDER BY cnt DESC
            """
        ).fetchall()


def stats_rentals_by_producer():
    with get_connection() as c:
        return c.execute(
            """
            SELECT m.producer AS label, COUNT(*) AS cnt
              FROM rentals r JOIN movies m ON m.id=r.movie_id
             GROUP BY m.producer
             ORDER BY cnt DESC
            """
        ).fetchall()
