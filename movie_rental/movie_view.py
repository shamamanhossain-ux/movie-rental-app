
import tkinter as tk
from tkinter import ttk, messagebox
from models import movies_list, movie_add, movie_update, movie_delete

class MovieView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._build_search()
        self._build_table()
        self._build_form()
        self.refresh()

    def _build_search(self):
        s = ttk.LabelFrame(self, text="Search Movies")
        s.pack(fill="x", padx=8, pady=6)
        self.inTitle = ttk.Entry(s, width=20); self._lrow(s,"Title:", self.inTitle, 0,0)
        self.inGenre = ttk.Entry(s, width=16); self._lrow(s,"Genre:", self.inGenre, 0,2)
        self.inProducer = ttk.Entry(s, width=16); self._lrow(s,"Producer:", self.inProducer, 0,4)
        self.inYear = ttk.Entry(s, width=10); self._lrow(s,"Year:", self.inYear, 1,0)
        self.inPMin = ttk.Entry(s, width=10); self._lrow(s,"Price Min:", self.inPMin, 1,2)
        self.inPMax = ttk.Entry(s, width=10); self._lrow(s,"Price Max:", self.inPMax, 1,4)
        ttk.Button(s, text="Search", command=self.search).grid(row=0, column=6, padx=6)
        ttk.Button(s, text="Clear", command=self.clear).grid(row=1, column=6, padx=6)

    def _build_table(self):
        wrap = ttk.Frame(self); wrap.pack(fill="both", expand=True, padx=8, pady=(0,6))
        cols=("id","title","genre","year","price","producer","avail")
        self.tv = ttk.Treeview(wrap, columns=cols, show="headings", height=12)
        heads={"id":"ID","title":"Title","genre":"Genre","year":"Year","price":"Price","producer":"Producer","avail":"Available"}
        for k,v in heads.items(): self.tv.heading(k, text=v)
        for k in cols: self.tv.column(k, width=100, anchor="w")
        self.tv.column("id", width=60, anchor="center")
        self.tv.pack(side="left", fill="both", expand=True)
        vs=ttk.Scrollbar(wrap,orient="vertical",command=self.tv.yview); self.tv.configure(yscroll=vs.set); vs.pack(side="right", fill="y")

    def _build_form(self):
        f = ttk.LabelFrame(self, text="Movie Form")
        f.pack(fill="x", padx=8, pady=6)
        self.fTitle=ttk.Entry(f,width=30); self._lrow(f,"Title:", self.fTitle,0,0)
        self.fGenre=ttk.Entry(f,width=20); self._lrow(f,"Genre:", self.fGenre,0,2)
        self.fYear=ttk.Entry(f,width=10); self._lrow(f,"Year:", self.fYear,0,4)
        self.fPrice=ttk.Entry(f,width=10); self._lrow(f,"Price:", self.fPrice,1,0)
        self.fProducer=ttk.Entry(f,width=20); self._lrow(f,"Producer:", self.fProducer,1,2)
        ttk.Button(f,text="Add",command=self.add).grid(row=0,column=6,padx=6)
        ttk.Button(f,text="Update Selected",command=self.update).grid(row=0,column=7,padx=6)
        ttk.Button(f,text="Delete Selected",command=self.delete).grid(row=1,column=6,padx=6)

    def _lrow(self, parent, lbl, widget, r, c):
        ttk.Label(parent,text=lbl).grid(row=r,column=c,sticky="w",padx=6,pady=3)
        widget.grid(row=r,column=c+1,sticky="w",padx=6,pady=3)

    def refresh(self):
        self._fill(movies_list())

    def search(self):
        def to_float(x):
            try: return float(x)
            except: return None
        y = self.inYear.get().strip()
        res = movies_list(
            title=self.inTitle.get().strip() or None,
            genre=self.inGenre.get().strip() or None,
            producer=self.inProducer.get().strip() or None,
            year=int(y) if y.isdigit() else None,
            price_min=to_float(self.inPMin.get().strip()),
            price_max=to_float(self.inPMax.get().strip())
        )
        self._fill(res)

    def clear(self):
        for e in (self.inTitle,self.inGenre,self.inProducer,self.inYear,self.inPMin,self.inPMax):
            e.delete(0,"end")
        self.refresh()

    def _fill(self, rows):
        for i in self.tv.get_children(): self.tv.delete(i)
        for r in rows:
            self.tv.insert("", "end", iid=r["id"], values=(
                r["id"], r["title"], r["genre"], r["release_year"],
                f"{r['rental_price']:.2f}", r["producer"], "Yes" if r["available"] else "No"
            ))

    def add(self):
        try:
            movie_add(self.fTitle.get().strip(), self.fGenre.get().strip(),
                      int(self.fYear.get()), float(self.fPrice.get()), self.fProducer.get().strip())
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        self.refresh(); messagebox.showinfo("OK","Movie added.")

    def update(self):
        sel = self.tv.selection()
        if not sel: messagebox.showwarning("Select", "Pick a movie row."); return
        mid = int(sel[0])
        try:
            movie_update(mid, self.fTitle.get().strip(), self.fGenre.get().strip(),
                        int(self.fYear.get()), float(self.fPrice.get()), self.fProducer.get().strip())
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        self.refresh(); messagebox.showinfo("OK","Movie updated.")

    def delete(self):
        sel = self.tv.selection()
        if not sel: messagebox.showwarning("Select", "Pick a movie row."); return
        mid = int(sel[0])
        if not messagebox.askyesno("Confirm", f"Delete movie ID {mid}?"): return
        try:
            movie_delete(mid)
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        self.refresh(); messagebox.showinfo("OK","Movie deleted.")
