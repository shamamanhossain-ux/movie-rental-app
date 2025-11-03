
import tkinter as tk
from tkinter import ttk, messagebox
from seed import bootstrap
from models import check_login
from movie_view import MovieView
from customer_view import CustomerView
from rental_view import RentalView
from reports import export_currently_rented, export_overdue, export_stats_by
from charts import show_genre_chart, show_producer_pie

APP_BG = "#0f4c75"

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Movie Rental Management System")
        self.geometry("1050x720")
        self.configure(bg=APP_BG)
        self._build_login()

    def _build_login(self):
        self.login_frame = tk.Frame(self, bg=APP_BG)
        self.login_frame.pack(expand=True)
        card = tk.Frame(self.login_frame, bg="white", padx=20, pady=20)
        card.pack()
        tk.Label(card, text="Login", font=("Segoe UI", 18, "bold")).grid(row=0,column=0,columnspan=2,pady=(0,10))
        tk.Label(card, text="Username:").grid(row=1,column=0,sticky="e", padx=6, pady=6)
        self.inUser = ttk.Entry(card, width=25); self.inUser.grid(row=1,column=1,padx=6, pady=6)
        tk.Label(card, text="Password:").grid(row=2,column=0,sticky="e", padx=6, pady=6)
        self.inPass = ttk.Entry(card, width=25, show="*"); self.inPass.grid(row=2,column=1,padx=6, pady=6)
        ttk.Button(card, text="Login", command=self._do_login).grid(row=3,column=0,columnspan=2,pady=(10,0))
        tk.Label(card, text="Demo users: admin/admin123, staff/staff123", fg="#666").grid(row=4,column=0,columnspan=2,pady=(8,0))

    def _do_login(self):
        if check_login(self.inUser.get().strip(), self.inPass.get().strip()):
            self.login_frame.destroy()
            self._build_shell()
        else:
            messagebox.showerror("Login failed", "Invalid credentials.")

    def _build_shell(self):
        header = tk.Frame(self, bg=APP_BG)
        header.pack(fill="x", pady=(8,4), padx=10)
        tk.Label(header, text="Movie Rental Management", bg=APP_BG, fg="white",
                 font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Button(header, text="Movie Management", command=lambda: self._switch_to('movie')).pack(side="right", padx=4)
        ttk.Button(header, text="Customer Management", command=lambda: self._switch_to('customer')).pack(side="right", padx=4)
        ttk.Button(header, text="Rental Management", command=lambda: self._switch_to('rental')).pack(side="right", padx=4)

        tools = tk.Frame(self, bg="#e9f0f7")
        tools.pack(fill="x", padx=10, pady=(0,8))
        ttk.Button(tools, text="Export: Currently Rented", command=export_currently_rented).pack(side="left", padx=4, pady=6)
        ttk.Button(tools, text="Export: Overdue", command=export_overdue).pack(side="left", padx=4)
        ttk.Button(tools, text="Export: Stats by Genre", command=lambda: export_stats_by('genre')).pack(side="left", padx=4)
        ttk.Button(tools, text="Export: Stats by Producer", command=lambda: export_stats_by('producer')).pack(side="left", padx=4)
        ttk.Button(tools, text="Chart: Rentals per Genre", command=show_genre_chart).pack(side="right", padx=4)
        ttk.Button(tools, text="Chart: Rentals by Producer", command=show_producer_pie).pack(side="right", padx=4)

        self.content = tk.Frame(self)
        self.content.pack(fill="both", expand=True, padx=10, pady=(0,10))

        self.frames = {
            'movie': MovieView(self.content),
            'customer': CustomerView(self.content),
            'rental': RentalView(self.content),
        }
        self._switch_to('rental')

    def _switch_to(self, key):
        for k, frame in self.frames.items():
            frame.pack_forget()
        self.frames[key].pack(fill="both", expand=True)

if __name__ == "__main__":
    bootstrap()
    App().mainloop()
