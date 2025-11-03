
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from models import rentals_list, available_movies, customers_list, issue_movie, return_movie, DATE_FMT

class RentalView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._toolbar()
        self._search()
        self._table()
        self.refresh()

    def _toolbar(self):
        bar = ttk.Frame(self)
        bar.pack(fill="x", padx=8, pady=(4,6))
        ttk.Button(bar, text="View Rentals", command=self.refresh).pack(side="left", padx=4)
        ttk.Button(bar, text="Rent a Movie", command=self.open_issue).pack(side="left", padx=4)
        ttk.Button(bar, text="Return a Movie", command=self.open_return).pack(side="left", padx=4)

    def _search(self):
        s = ttk.LabelFrame(self, text="Search Rentals")
        s.pack(fill="x", padx=8, pady=6)
        self.inCust=ttk.Entry(s,width=22); self._lrow(s,"Customer Name:", self.inCust,0,0)
        self.inMovie=ttk.Entry(s,width=22); self._lrow(s,"Movie Title:", self.inMovie,0,2)
        self.inIssue=ttk.Entry(s,width=14); self._lrow(s,"Issue (YYYY-MM-DD):", self.inIssue,1,0)
        self.inReturn=ttk.Entry(s,width=14); self._lrow(s,"Return (YYYY-MM-DD):", self.inReturn,1,2)
        ttk.Button(s,text="Search",command=self.search).grid(row=0,column=6,padx=6)
        ttk.Button(s,text="Clear",command=self.clear).grid(row=1,column=6,padx=6)

    def _table(self):
        wrap = ttk.Frame(self); wrap.pack(fill="both", expand=True, padx=8, pady=(0,8))
        cols=("id","customer","movie","issue","due","ret","fee")
        self.tv = ttk.Treeview(wrap, columns=cols, show="headings", height=15)
        heads={"id":"Issue #","customer":"Customer","movie":"Movie","issue":"Issue Date","due":"Due Date","ret":"Return Date","fee":"Late Fee ($)"}
        for k,v in heads.items(): self.tv.heading(k,text=v)
        for k in cols: self.tv.column(k, width=110, anchor="w")
        self.tv.column("id", width=70, anchor="center")
        self.tv.pack(side="left", fill="both", expand=True)
        vs=ttk.Scrollbar(wrap,orient="vertical",command=self.tv.yview); self.tv.configure(yscroll=vs.set); vs.pack(side="right", fill="y")

    def _lrow(self,parent,lbl,widget,r,c):
        ttk.Label(parent,text=lbl).grid(row=r,column=c,sticky="w",padx=6,pady=3)
        widget.grid(row=r,column=c+1,sticky="w",padx=6,pady=3)

    def refresh(self):
        self._fill(rentals_list())

    def search(self):
        self._fill(rentals_list(
            customer=self.inCust.get().strip() or None,
            movie=self.inMovie.get().strip() or None,
            issue=self.inIssue.get().strip() or None,
            ret=self.inReturn.get().strip() or None
        ))

    def clear(self):
        for e in (self.inCust,self.inMovie,self.inIssue,self.inReturn): e.delete(0,"end")
        self.refresh()

    def _fill(self, rows):
        for i in self.tv.get_children(): self.tv.delete(i)
        for r in rows:
            self.tv.insert("", "end", iid=r["id"], values=(
                r["id"], r["customer"], r["movie"], r["issue_date"], r["due_date"],
                r["return_date"] or "", f"{r['late_fee']:.2f}"
            ))

    def open_issue(self):
        IssueDialog(self)

    def open_return(self):
        sel=self.tv.selection()
        rid=int(sel[0]) if sel else None
        ReturnDialog(self, rid)

class IssueDialog(tk.Toplevel):
    def __init__(self, master: RentalView):
        super().__init__(master)
        self.title("Rent a Movie"); self.resizable(False,False); self.grab_set()
        self.customers = customers_list()
        self.movies = available_movies()
        f = ttk.Frame(self, padding=10); f.pack(fill="both", expand=True)
        ttk.Label(f,text="Customer:").grid(row=0,column=0,sticky="w",pady=4)
        self.cbCust=ttk.Combobox(f,width=35, state="readonly",
                                 values=[f"{r['id']} – {r['name']}" for r in self.customers])
        self.cbCust.grid(row=0,column=1,padx=6)
        ttk.Label(f,text="Movie:").grid(row=1,column=0,sticky="w",pady=4)
        self.cbMovie=ttk.Combobox(f,width=35, state="readonly",
                                  values=[f"{r['id']} – {r['title']}" for r in self.movies])
        self.cbMovie.grid(row=1,column=1,padx=6)
        today = datetime.today().date()
        ttk.Label(f,text="Issue (YYYY-MM-DD):").grid(row=2,column=0,sticky="w",pady=4)
        self.enIssue=ttk.Entry(f,width=18); self.enIssue.insert(0,today.strftime(DATE_FMT)); self.enIssue.grid(row=2,column=1,sticky="w")
        ttk.Label(f,text="Due (YYYY-MM-DD):").grid(row=3,column=0,sticky="w",pady=4)
        self.enDue=ttk.Entry(f,width=18); self.enDue.insert(0,(today+timedelta(days=7)).strftime(DATE_FMT)); self.enDue.grid(row=3,column=1,sticky="w")
        row = ttk.Frame(f); row.grid(row=4,column=0,columnspan=2,pady=(8,0))
        ttk.Button(row,text="Cancel",command=self.destroy).pack(side="right",padx=4)
        ttk.Button(row,text="Save",command=self._save).pack(side="right",padx=4)
    def _save(self):
        if not self.cbCust.get() or not self.cbMovie.get():
            messagebox.showwarning("Missing","Select customer and movie"); return
        cust_id=int(self.cbCust.get().split(" – ")[0]); mov_id=int(self.cbMovie.get().split(" – ")[0])
        try:
            issue_movie(cust_id, mov_id, self.enIssue.get().strip(), self.enDue.get().strip())
        except Exception as e:
            messagebox.showerror("Error",str(e)); return
        self.master.refresh(); messagebox.showinfo("OK","Issued"); self.destroy()

class ReturnDialog(tk.Toplevel):
    def __init__(self, master: RentalView, rental_id=None):
        super().__init__(master)
        self.title("Return a Movie"); self.resizable(False,False); self.grab_set()
        f=ttk.Frame(self,padding=10); f.pack(fill="both", expand=True)
        ttk.Label(f,text="Rental ID:").grid(row=0,column=0,sticky="w",pady=4)
        self.enId=ttk.Entry(f,width=10); self.enId.grid(row=0,column=1,sticky="w")
        if rental_id: self.enId.insert(0,str(rental_id))
        ttk.Label(f,text="Return (YYYY-MM-DD):").grid(row=1,column=0,sticky="w",pady=4)
        self.enRet=ttk.Entry(f,width=18); self.enRet.insert(0, datetime.today().strftime(DATE_FMT)); self.enRet.grid(row=1,column=1,sticky="w")
        row=ttk.Frame(f); row.grid(row=2,column=0,columnspan=2,pady=(8,0))
        ttk.Button(row,text="Cancel",command=self.destroy).pack(side="right",padx=4)
        ttk.Button(row,text="Save",command=self._save).pack(side="right",padx=4)
    def _save(self):
        rid=self.enId.get().strip()
        if not rid: messagebox.showwarning("Missing","Enter Rental ID"); return
        try:
            fee=return_movie(int(rid), self.enRet.get().strip())
        except Exception as e:
            messagebox.showerror("Error",str(e)); return
        self.master.refresh(); messagebox.showinfo("OK", f"Returned. Late fee: ${fee:.2f}"); self.destroy()
