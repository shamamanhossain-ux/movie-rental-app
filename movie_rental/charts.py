
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from models import stats_rentals_per_genre, stats_rentals_by_producer

def show_genre_chart():
    rows = stats_rentals_per_genre()
    labels = [r["label"] or "Unknown" for r in rows]
    counts = [r["cnt"] for r in rows]
    plt.figure()
    plt.bar(labels, counts)
    plt.title("Rentals per Genre")
    plt.xlabel("Genre")
    plt.ylabel("Rentals")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.show()

def show_producer_pie():
    rows = stats_rentals_by_producer()
    labels = [r["label"] or "Unknown" for r in rows]
    counts = [r["cnt"] for r in rows]
    plt.figure()
    plt.pie(counts, labels=labels, autopct="%1.0f%%")
    plt.title("Rental Share by Producer")
    plt.tight_layout()
    plt.show()
