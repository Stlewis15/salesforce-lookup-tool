# 🚀 Salesforce Lookup Tool (Python + CustomTkinter + OAuth) 
### Author: [Lewis Stargill (Stlewis15)](https://github.com/Stlewis15)

---

## 🧠 Overview

The **Salesforce Lookup Tool** is a Python-based desktop application built to help engineering and sales teams quickly search Salesforce records (Construction Requests, Inside Wiring Surveys, and Phone Line Details) without logging into the Salesforce web UI.

Originally designed for **WOW! (WideOpenWest)** engineers, this tool provided a **fast, lightweight, and secure GUI** alternative for querying Salesforce Lighting data using **OAuth2 with OneLogin SSO**.

---

## 🧩 Key Features

✅ **Modern GUI:**  
Built using [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — a modern, customizable Python GUI framework that makes Tkinter interfaces sleek and professional.

✅ **Secure Salesforce OAuth2 Authentication:**  
Integrates with **OneLogin SSO** using Salesforce’s OAuth2 API for safe, user-based authentication — no hardcoded passwords or tokens.

✅ **Dynamic Queries:**  
Users can quickly pull Salesforce data from three major object groups:
- 🏗️ `Construction__c` – Construction and Part Quote Requests  
- 🔌 `Sales_Request__c` – Inside Wiring and SRQs  
- ☎️ `Phone_Line_Detail__c` – Hosted VoIP line details

✅ **Smart Filtering:**  
Search by **address**, **phone number**, or **partial matches** for flexible and human-friendly querying.

✅ **Data Export:**  
Instantly export query results to `.csv` or `.xlsx` format for use in Excel or reports.

✅ **User-Specific Login:**  
Displays the logged-in user's name (via SSO) dynamically on the app window.

✅ **Session Controls:**  
Includes a clean **Logout** button and session clearing to maintain Salesforce data security.

---

## 💡 Technical Highlights

This project demonstrates practical use of **Python** in real enterprise workflows.

| Category | Technology / Concept | Description |
|-----------|----------------------|--------------|
| 🖥️ GUI Framework | **CustomTkinter** | Used for building a clean, modern interface (light/dark themes, responsive layout). |
| 🔐 Authentication | **Salesforce OAuth2 + OneLogin SSO** | Enables secure login via browser — no manual tokens required. |
| 🔗 API Access | **Simple-Salesforce** | Python package for querying Salesforce using SOQL statements. |
| 📊 Data Handling | **Pandas DataFrame** | Organizes Salesforce query results into tabular data for easy export and display. |
| 💾 Export Formats | **CSV / Excel Writer** | Users can save data directly to Excel or CSV from within the app. |
| 🧠 Programming Concepts | Functions, Classes, Exception Handling | Demonstrates modular programming, error handling, and event-driven design. |

---

## 🧱 Architecture

**Core File:**  
`main_oauth.py` — contains all GUI, authentication, and query logic.  

**Key Components:**
- `connect_salesforce_oauth()` → handles SSO OAuth login flow  
- `SalesforceApp()` → main class that controls GUI  
- `query_construction()`, `query_sales_requests()`, `query_phone_lines()` → SOQL data retrieval  
- `export_to_csv()` & `export_to_excel()` → data export functions  

---

## 🧭 Example Screenshots

### 🔹 Query Interface
![Query Window](screenshots/app_ui_query.png)

### 🔹 Legacy Salesforce Token Login (v1)
![Legacy Token Login](screenshots/v1_salesforce_token_login.png)

### 🔹 Updated OneLogin SSO OAuth (v2)
![OAuth Login](screenshots/v2_oauth_onelogin_screen.png)

---

## 🔧 How to Run Locally

**Requirements:**
- Python 3.10+
- Installed modules:
  ```bash
  pip install customtkinter simple-salesforce pandas requests requests-oauthlib pillow

