
import sqlite3
import pandas as pd
from tkinter import messagebox

DB_NAME = "rentals.db"

def export_currently_rented():
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT r.id AS Issue_ID, c.name AS Customer, m.title AS Movie,
           r.issue_date AS Issue_Date, r.due_date AS Due_Date
    FROM rentals r
    JOIN customers c ON r.customer_id = c.id
    JOIN movies m ON r.movie_id = m.id
    WHERE r.return_date IS NULL
    """
    df = pd.read_sql_query(query, conn)
    df.to_excel("currently_rented.xlsx", index=False)
    conn.close()
    messagebox.showinfo("Export", "✅ Exported currently_rented.xlsx")


def export_overdue():
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT r.id AS Issue_ID, c.name AS Customer, m.title AS Movie,
           r.issue_date AS Issue_Date, r.due_date AS Due_Date
    FROM rentals r
    JOIN customers c ON r.customer_id = c.id
    JOIN movies m ON r.movie_id = m.id
    WHERE r.return_date IS NULL AND date(r.due_date) < date('now')
    """
    df = pd.read_sql_query(query, conn)
    df.to_excel("overdue_rentals.xlsx", index=False)
    conn.close()
    messagebox.showinfo("Export", "✅ Exported overdue_rentals.xlsx")


def export_stats_by_genre():
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT m.genre AS Genre, COUNT(*) AS Rentals
    FROM rentals r
    JOIN movies m ON r.movie_id = m.id
    GROUP BY m.genre
    """
    df = pd.read_sql_query(query, conn)
    df.to_excel("stats_by_genre.xlsx", index=False)
    conn.close()
    messagebox.showinfo("Export", "✅ Exported stats_by_genre.xlsx")


def export_stats_by_producer():
    conn = sqlite3.connect(DB_NAME)
    query = """
    SELECT m.producer AS Producer, COUNT(*) AS Rentals
    FROM rentals r
    JOIN movies m ON r.movie_id = m.id
    GROUP BY m.producer
    """
    df = pd.read_sql_query(query, conn)
    df.to_excel("stats_by_producer.xlsx", index=False)
    conn.close()
    messagebox.showinfo("Export", "✅ Exported stats_by_producer.xlsx")
