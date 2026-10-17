import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "customer360")
API_BASE = os.getenv("API_BASE", "https://dummyjson.com")

CUSTOMERS_COL = "customers"
PRODUCTS_COL = "products"
ORDERS_COL = "carts"

if not MONGO_URI:
    raise ValueError("MONGO_URI not found. Check your .env file.")
