import requests
from pymongo import MongoClient
from config.settings import (
    API_BASE, MONGO_URI, DB_NAME,
    CUSTOMERS_COL, PRODUCTS_COL, ORDERS_COL
)

def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def fetch(endpoint, key):
    url = f"{API_BASE}/{endpoint}?limit=0"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()[key]

def load_collection(db, collection_name, records):
    col = db[collection_name]
    col.delete_many({})
    if records:
        col.insert_many(records)
    print(f"Loaded {len(records)} docs into {collection_name}")

def main():
    db = get_db()
    print("Fetching users...")
    load_collection(db, CUSTOMERS_COL, fetch("users", "users"))
    print("Fetching products...")
    load_collection(db, PRODUCTS_COL, fetch("products", "products"))
    print("Fetching carts...")
    load_collection(db, ORDERS_COL, fetch("carts", "carts"))
    print("Done. Data is in MongoDB Atlas.")

if __name__ == "__main__":
    main()
