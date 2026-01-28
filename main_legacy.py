import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
from simple_salesforce import Salesforce
import pandas as pd

# --------------------- LOGIN HANDLER ---------------------
def connect_salesforce(username, password, token):
    try:
        sf = Salesforce(username=username, password=password, security_token=token, domain='login')
        messagebox.showinfo("Success", "Connected to Salesforce successfully!")
        return sf
    except Exception as e:
        messagebox.showerror("Login Failed", str(e))
        return None

# --------------------- QUERY FUNCTIONS ---------------------
def query_construction(sf, address, zipcode):
    soql = f"""
    SELECT Name, Opportunity__r.Name, Stage__c, Quote_Status__c, Transport__c,
           Final_Coax_Cost__c, Final_Fiber_Cost__c, Network_Cost__c, Address__c
    FROM Construction__c
    WHERE Address__c LIKE '%{address}%'
    LIMIT 200
    """
    return sf.query_all(soql)['records']

def query_sales_requests(sf, address, zipcode):
    soql = f"""
    SELECT Name, SRQ_Status__c, SRQ_Type__c, Assigned_To__c, Fiber_Costs__c, 
           Coax_Costs__c, Address__c
    FROM Sales_Request__c
    WHERE Address__c LIKE '%{address}%'
    LIMIT 200
    """
    return sf.query_all(soql)['records']

def query_phone_lines(sf, address, phone):
    soql = f"""
    SELECT Name, Phone_Number__c, Customer_Name__c, Hunt_Group__c, Auto_Attendant__c,
           Address__c
    FROM Phone_Line_Detail__c
    WHERE (Service_Type__c = 'Hosted VOIP')
    AND (Address__c LIKE '%{address}%' OR Phone_Number__c LIKE '%{phone}%')
    LIMIT 200
    """
    return sf.query_all(soql)['records']

# --------------------- EXPORT FUNCTIONS ---------------------
def export_to_csv(dataframe):
    file = filedialog.asksaveasfilename(defaultextension=".csv")
    if file:
        dataframe.to_csv(file, index=False)
        messagebox.showinfo("Exported", f"Data saved to {file}")

def export_to_excel(dataframe):
    file = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if file:
        dataframe.to_excel(file, index=False)
        messagebox.showinfo("Exported", f"Data saved to {file}")

# --------------------- GUI ---------------------
class SalesforceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Salesforce SRQ+ Tool")
        self.geometry("900x600")
        self.sf = None
        self.create_login_tab()

    def create_login_tab(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True)

        login_tab = self.tabview.add("Login")
        query_tab = self.tabview.add("Query")

        # Login Tab
        ctk.CTkLabel(login_tab, text="Salesforce Username").pack(pady=5)
        self.username_entry = ctk.CTkEntry(login_tab, width=300)
        self.username_entry.pack()

        ctk.CTkLabel(login_tab, text="Password").pack(pady=5)
        self.password_entry = ctk.CTkEntry(login_tab, show="*", width=300)
        self.password_entry.pack()

        ctk.CTkLabel(login_tab, text="Security Token").pack(pady=5)
        self.token_entry = ctk.CTkEntry(login_tab, width=300)
        self.token_entry.pack()

        ctk.CTkButton(login_tab, text="Connect", command=self.login).pack(pady=20)

        # Query Tab
        ctk.CTkLabel(query_tab, text="Street Address").pack()
        self.address_entry = ctk.CTkEntry(query_tab, width=300)
        self.address_entry.pack()

        ctk.CTkLabel(query_tab, text="Zip Code / Phone (for PLD)").pack()
        self.zip_entry = ctk.CTkEntry(query_tab, width=300)
        self.zip_entry.pack()

        self.query_type = ctk.CTkOptionMenu(query_tab, values=[
            "Part Quote Request",
            "Inside Wiring Survey",
            "Phone Line Details"
        ])
        self.query_type.pack(pady=10)

        ctk.CTkButton(query_tab, text="Run Query", command=self.run_query).pack(pady=10)
        ctk.CTkButton(query_tab, text="Export CSV", command=lambda: export_to_csv(self.df)).pack(pady=5)
        ctk.CTkButton(query_tab, text="Export Excel", command=lambda: export_to_excel(self.df)).pack(pady=5)

        # Table
        self.tree = ttk.Treeview(query_tab)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    def login(self):
        u = self.username_entry.get()
        p = self.password_entry.get()
        t = self.token_entry.get()
        self.sf = connect_salesforce(u, p, t)

    def run_query(self):
        if not self.sf:
            messagebox.showerror("Error", "Please login first.")
            return

        address = self.address_entry.get()
        zip_or_phone = self.zip_entry.get()
        qtype = self.query_type.get()

        if qtype == "Part Quote Request":
            data = query_construction(self.sf, address, zip_or_phone)
        elif qtype == "Inside Wiring Survey":
            data = query_sales_requests(self.sf, address, zip_or_phone)
        else:
            data = query_phone_lines(self.sf, address, zip_or_phone)

        if not data:
            messagebox.showinfo("No Results", "No matching records found.")
            return

        # Convert to dataframe
        self.df = pd.DataFrame([{k: v for k, v in rec.items() if not isinstance(v, dict)} for rec in data])

        # Display in table
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(self.df.columns)
        self.tree["show"] = "headings"
        for col in self.df.columns:
            self.tree.heading(col, text=col)
        for row in self.df.to_numpy().tolist():
            self.tree.insert("", "end", values=row)

if __name__ == "__main__":
    app = SalesforceApp()
    app.mainloop()
