

import customtkinter as ctk
from tkinter import simpledialog
from tkinter import ttk, filedialog, messagebox
from simple_salesforce import Salesforce
import pandas as pd
import requests


ctk.set_appearance_mode("system")   # Options: "light", "dark", or "system"
ctk.set_default_color_theme("dark-blue")  # Options: "blue", "green", "dark-blue"

# --------------------- LOGIN HANDLER (OAUTH) ---------------------
from requests_oauthlib import OAuth2Session
from simple_salesforce import Salesforce
import webbrowser

# These will be provided by your Connected App
CLIENT_ID = "YOUR_CONSUMER_KEY_HERE"
CLIENT_SECRET = "YOUR_CONSUMER_SECRET_HERE"
REDIRECT_URI = "http://localhost:8080/callback"
TOKEN_URL = "https://login.salesforce.com/services/oauth2/token"
AUTH_URL = "https://login.salesforce.com/services/oauth2/authorize"
SCOPES = ["api", "refresh_token", "offline_access"]

def connect_salesforce_oauth():
    """Perform OAuth login through Salesforce + OneLogin SSO."""
    try:
        oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
        authorization_url, state = oauth.authorization_url(AUTH_URL)
        webbrowser.open(authorization_url)
        messagebox.showinfo("Action Required", "Please complete login in your browser. When finished, copy and paste the full redirected URL below into this window.")
        redirect_response = simpledialog.askstring("OAuth Login", "Paste the full redirected URL here:")
        
        token = oauth.fetch_token(
            TOKEN_URL,
            client_secret=CLIENT_SECRET,
            authorization_response=redirect_response
        )

        # Get user info from Salesforce Identity endpoint
        user_info_url = "https://login.salesforce.com/services/oauth2/userinfo"
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        user_info = requests.get(user_info_url, headers=headers).json()

        # Extract first name and first initial of last name
        first_name = user_info.get("given_name", "")
        last_initial = user_info.get("family_name", "")[:1]
        user_display = f"{first_name} {last_initial}." if last_initial else first_name

        # Create Salesforce connection
        sf = Salesforce(instance_url=token["instance_url"], session_id=token["access_token"])

        messagebox.showinfo("Success", f"You’re now logged in, {user_display}!")
        return sf, user_display

    except Exception as e:
        messagebox.showerror("Login Failed", str(e))
        return None, None



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
        self.title("Salesforce Lookup Tool")
        self.geometry("900x600")
        self.iconbitmap("wow.ico")
        self.sf = None

        # ----- WOW Banner Section -----
        from PIL import Image
        self.original_banner = Image.open("wow_banner.png")
        self.banner_photo = ctk.CTkImage(self.original_banner, size=(900, 80))
        self.banner_label = ctk.CTkLabel(self, image=self.banner_photo, text="")

        self.banner_label.pack(fill="x", pady=(20, 10))

        # ----- User Label (top-right) -----
        self.user_label = ctk.CTkLabel(
            self,
            text="",             
            font=("Arial", 12, "italic"),
            text_color="#555555",
            anchor="e"
        )
        self.user_label.place(relx=0.98, rely=0.08, anchor="ne")

        # ----- Dynamic color change for light/dark mode -----
        def update_label_color(*args):
            mode = ctk.get_appearance_mode()
            if mode == "Light":
                self.user_label.configure(text_color="#555555")
            else:
                self.user_label.configure(text_color="#DDDDDD")

        update_label_color()
        self.bind("<Configure>", lambda e: update_label_color())


        # ----- Flat-Style Logout Button -----
        self.logout_button = ctk.CTkButton(
            self,
            text="Logout",
            font=("Arial", 12),
            width=70,
            height=26,
            fg_color="transparent",
            hover_color="#E65C00",
            text_color="#FF5F00",
            border_width=1,
            border_color="#FF5F00",
            command=self.logout_user  # ← references method below
        )
        self.logout_button.place(relx=0.87, rely=0.08, anchor="ne")
        self.logout_button.place_forget()

        # ----- Subtitle -----
        subtitle = ctk.CTkLabel(
            self,
            text="Engineering Salesforce Lookup Tool",
            font=("Arial", 14, "bold"),
            text_color="#333333"
        )
        subtitle.pack(pady=(0, 20))

        # Bind window resize event
        self.bind("<Configure>", self.resize_banner)

        # Continue building UI
        self.create_login_tab()


    # ----------------------------------------
    def logout_user(self):
        """Clear Salesforce session and hide user info."""
        confirm = messagebox.askyesno("Logout", "Are you sure you want to log out?")
        if confirm:
            self.sf = None
            self.user_label.configure(text="")
            self.logout_button.place_forget()
            messagebox.showinfo("Logged Out", "You have been successfully logged out.")

        


    def create_login_tab(self):
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, pady=(60, 0))


        login_tab = self.tabview.add("Login")
        query_tab = self.tabview.add("Query")

        # Login Tab
        ctk.CTkLabel(login_tab, text="Sign in with OneLogin SSO credentials").pack(pady=10)
        ctk.CTkButton(login_tab, text="Login with Salesforce SSO", command=self.login).pack(pady=20)


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
        sf_conn, user_display = connect_salesforce_oauth()
        if sf_conn:
            self.sf = sf_conn
            # Update the user label on the header
            self.user_label.configure(text=f"Logged in as {user_display}")
            self.logout_button.place(relx=0.87, rely=0.08, anchor="ne")


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

    def resize_banner(self, event):
        """Dynamically resize the WOW banner when the window is resized."""
        try:
            new_width = event.width
            aspect_ratio = self.original_banner.height / self.original_banner.width
            new_height = int(new_width * aspect_ratio)

            resized = self.original_banner.resize((new_width, new_height))
            self.banner_photo = ImageTk.PhotoImage(resized)
            self.banner_label.configure(image=self.banner_photo)
            self.banner_label.image = self.banner_photo  # prevent garbage collection
        except Exception:
            pass


if __name__ == "__main__":
  
    app = SalesforceApp()
    app.mainloop()

