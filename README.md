# **Pantry Inventory Review And Tracking Enhancement (P.I.R.A.T.E.)**


## **Overview**

P.I.R.A.T.E. is a web-based application designed to automate the Pirate Pantry's inventory management system. It provides a role-based interface for students to browse and check out available items, and for authorized users to restock items, manage the inventory, and monitor pantry usage statistics. <br>

This project is developed to enhance efficiency and reduce workload on manual tracking, aiming to improve user experience for both students and the Pirate Pantry team.
<br>


## **Role-based Access Control**

### **User (Student)**
*   Log in using SU email
*   Search for available pantry items
*   Add or remove items from cart
*   Review cart and Confirm checkout

### **Trusted (Student Workers)**
*   All user features
*   Add new products to inventory
*   Update product quantities/information
*   Remove products
*   Manage product tags and brands

### **Admins**
*   All trusted features
*   Export usage statistics as PDF
*   Manage user access levels
<br>

## **Tech Stack**

### **Front End**
*   React + Typescript
*   Google OAuth

### **Back End**
*   Python (Flask REST API)

### **Database**
*   SQLite3 (Custom database modules)
<br>

## **Project Structure**

```
backend/
  ├── api.py          # Flask API endpoints
  ├── database.py     # SQLite3 database logic
  ├── main.py         # Application entry point
  ├── common.py       # Shared utilities
  ├── misc.py         # Helper functions
  ├── stats.py        # Analytics / reporting logic
  ├── wsgi.py         # Deployment entry (WSGI)
  ├── requirements.txt
  ├── migrations/     # Database schema migrations
  │    ├── 0001_init_schema.sql
  │    └── ...
  └── tests/          # Pytest test
       ├── test_api.py
       └── test_database.py

frontend/
  ├── public/
  │    └── _redirects
  └── src/
       ├── auth/       # Authentication components
       ├── checkout/   # Cart & checkout flow
       ├── css_defaults/
       ├── misc/
       ├── workpanel/  # Admin interface
       ├── API.tsx     # API communication layer
       └── App.css
```
<br>

## **Database Schema**

The system uses SQLite3 with the following schema:

### **Pantry Inventory**
*   `products`: Stores item information (id, name, brand, quantity, image_link)
*   `brands`: Stores product brands
*   `tags`: Stores product tag labels
*   `product_tags`: Many-to-many relationship between products and tags
*   `image_links`: Stores image paths for products
### **Users & Authentication**
*   `users`: Stores user accounts and access levels (trusted, admin)
*   `auth_sessions`: Manages login sessions and tokens
*   `auth_codes`: Temporary authentication codes
### **Checkout Activity**
*   `total_checkouts`: Records completed checkouts including checkout id, item details, checkout quantity and time.
<br>

## **API Overview**
The REST API is built using Python Flask and incorporated with role-based access control authentication.
<br>

### **Example endpoints**
**Products: /products**
*   GET /products: List/filter/search for products (Role: Any)
*   POST /products: Add or update products (Role: Trusted, Admin)
*   DELETE /products — Remove products by ids (Role: Trusted, Admin)
*   PATCH /products/checkout — Checkout items (Role: Any)
*   GET /products/available: List of available products from pantry (Role: Any)

## **Prerequisites**

*   Python 3.10+
*   pip
*   Google OAuth Credentials (client ID and secret)
<br>


## **Setup**
**1.   Clone the repository**

```
git clone <repo-url>
cd /workspaces/Pirate-Pantry-Inventory-Tracking
```


**4.   Set environment variables: Create a `.env` file and configure necessary variables.**
<br>

**5.   Run the local deployment**

```
localhost.bat   # Windows
localhost.sh    # Mac/Linux
```
<br>



## **Testing**

Tests cover:

*   API endpoints
*   Database functionality
*   Admin access control
<br>

Run tests using pytest:

```
python -m pytest backend/tests/
```
<br>

## **Deployment**

*   Frontend:	Cloudfare	(Add `.env` variables)
*   Backend	API: Pythonanywhere.com
*   Database: Cloudfare
<br>

## **Contributors**

### **Students**
*    Camile James
*    Nhi "Amy" Tran
*    Cade Doehler
*    Aidan Fitzgerald

### **Faculty Advisor**
*   Dr. Barbara Anthony
<br>


## **Acknowledgements**

*   Southwestern University
*   Dr.  Anthony
*   Dr. Mikan and Pirate Pantry team
<br>

## **Liscense**
<br>
This project is for educational use and deployment at Southwestern University.
