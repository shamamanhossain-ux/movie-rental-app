
import tkinter as tk
from tkinter import ttk, messagebox
from models import customers_list, customer_add, customer_update, customer_delete

class CustomerView(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self._build_search()
        self._build_table()
        self._build_form()
        self.refresh()

    def _build_search(self):
        s = ttk.LabelFrame(self, text="Search Customers")
        s.pack(fill="x", padx=8, pady=6)
        self.inName = ttk.Entry(s, width=22); self._lrow(s,"Name:", self.inName, 0,0)
        self.inID = ttk.Entry(s, width=10); self._lrow(s,"ID:", self.inID, 0,2)
        ttk.Button(s, text="Search", command=self.search).grid(row=0,column=4,padx=6)
        ttk.Button(s, text="Clear", command=self.clear).grid(row=0,column=5,padx=6)

    def _build_table(self):
        wrap = ttk.Frame(self); wrap.pack(fill="both", expand=True, padx=8, pady=(0,6))
        cols=("id","name","contact")
        self.tv = ttk.Treeview(wrap, columns=cols, show="headings", height=12)
        for k,lbl in {"id":"ID","name":"Name","contact":"Contact"}.items(): self.tv.heading(k,text=lbl)
        self.tv.column("id", width=60, anchor="center")
        self.tv.pack(side="left", fill="both", expand=True)
        vs=ttk.Scrollbar(wrap,orient="vertical",command=self.tv.yview); self.tv.configure(yscroll=vs.set); vs.pack(side="right", fill="y")

    def _build_form(self):
        f = ttk.LabelFrame(self, text="Customer Form")
        f.pack(fill="x", padx=8, pady=6)
        self.fName=ttk.Entry(f,width=30); self._lrow(f,"Name:", self.fName,0,0)
        self.fContact=ttk.Entry(f,width=30); self._lrow(f,"Contact:", self.fContact,0,2)
        ttk.Button(f,text="Add",command=self.add).grid(row=0,column=6,padx=6)
        ttk.Button(f,text="Update Selected",command=self.update).grid(row=0,column=7,padx=6)
        ttk.Button(f,text="Delete Selected",command=self.delete).grid(row=0,column=8,padx=6)

    def _lrow(self,parent,lbl,widget,r,c):
        ttk.Label(parent,text=lbl).grid(row=r,column=c,sticky="w",padx=6,pady=3)
        widget.grid(row=r,column=c+1,sticky="w",padx=6,pady=3)

    def refresh(self):
        self._fill(customers_list())

    def search(self):
        cid = int(self.inID.get()) if self.inID.get().strip().isdigit() else None
        self._fill(customers_list(q_name=self.inName.get().strip() or None, q_id=cid))

    def clear(self):
        for e in (self.inName,self.inID): e.delete(0,"end")
        self.refresh()

    def _fill(self, rows):
        for i in self.tv.get_children(): self.tv.delete(i)
        for r in rows:
            self.tv.insert("", "end", iid=r["id"], values=(r["id"], r["name"], r["contact"]))

    def add(self):
        try:
            customer_add(self.fName.get().strip(), self.fContact.get().strip())
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        self.refresh(); messagebox.showinfo("OK","Customer added.")

    def update(self):
        sel = self.tv.selection()
        if not sel: messagebox.showwarning("Select", "Pick a customer row."); return
        cid = int(sel[0])
        try:
            customer_update(cid, self.fName.get().strip(), self.fContact.get().strip())
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        self.refresh(); messagebox.showinfo("OK","Customer updated.")

    def delete(self):
        sel = self.tv.selection()
        if not sel: messagebox.showwarning("Select", "Pick a customer row."); return
        cid=int(sel[0])
        if not messagebox.askyesno("Confirm", f"Delete customer ID {cid}?"): return
        try:
            customer_delete(cid)
        except Exception as e:
            messagebox.showerror("Error", str(e)); return
        self.refresh(); messagebox.showinfo("OK","Customer deleted.")
