import pandas as pd
from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME

def get_db():
    return MongoClient(MONGO_URI)[DB_NAME]

def run():
    db = get_db()

    # 1. Customers — flatten nested fields
    customers = list(db['customers'].find({}, {'_id': 0}))
    cust_rows = []
    for c in customers:
        cust_rows.append({
            'customer_id': c.get('id'),
            'first_name': c.get('firstName'),
            'last_name': c.get('lastName'),
            'age': c.get('age'),
            'gender': c.get('gender'),
            'email': c.get('email'),
            'city': (c.get('address') or {}).get('city'),
            'state': (c.get('address') or {}).get('state'),
            'country': (c.get('address') or {}).get('country'),
            'company': (c.get('company') or {}).get('name'),
            'department': (c.get('company') or {}).get('department'),
            'recency': c.get('recency'),
            'frequency': c.get('frequency'),
            'monetary': c.get('monetary'),
            'r_score': c.get('r_score'),
            'f_score': c.get('f_score'),
            'm_score': c.get('m_score'),
            'rfm_score': c.get('rfm_score'),
            'segment': c.get('segment'),
            'churned': c.get('churned'),
            'churn_probability': c.get('churn_probability'),
            'churn_risk': c.get('churn_risk')
        })
    pd.DataFrame(cust_rows).to_csv('data/processed/customers.csv', index=False)
    print('customers.csv:', len(cust_rows), 'rows')

    # 2. Orders — flatten product arrays
    orders = list(db['orders'].find({}, {'_id': 0}))
    order_rows = []
    for o in orders:
        order_rows.append({
            'order_id': o.get('order_id'),
            'customer_id': o.get('customer_id'),
            'order_date': o.get('order_date'),
            'status': o.get('status'),
            'total': o.get('total'),
            'total_products': o.get('total_products'),
            'total_quantity': o.get('total_quantity')
        })
    pd.DataFrame(order_rows).to_csv('data/processed/orders.csv', index=False)
    print('orders.csv:', len(order_rows), 'rows')

    # 3. Order items (line-level, for product analysis)
    item_rows = []
    for o in orders:
        for p in o.get('products', []):
            item_rows.append({
                'order_id': o.get('order_id'),
                'customer_id': o.get('customer_id'),
                'order_date': o.get('order_date'),
                'status': o.get('status'),
                'product_id': p.get('id'),
                'product_title': p.get('title'),
                'unit_price': p.get('price'),
                'quantity': p.get('quantity'),
                'line_total': p.get('total')
            })
    pd.DataFrame(item_rows).to_csv('data/processed/order_items.csv', index=False)
    print('order_items.csv:', len(item_rows), 'rows')

    # 4. Products
    products = list(db['products'].find({}, {'_id': 0}))
    prod_rows = []
    for p in products:
        prod_rows.append({
            'product_id': p.get('id'),
            'title': p.get('title'),
            'category': p.get('category'),
            'price': p.get('price'),
            'rating': p.get('rating'),
            'stock': p.get('stock'),
            'brand': p.get('brand')
        })
    pd.DataFrame(prod_rows).to_csv('data/processed/products.csv', index=False)
    print('products.csv:', len(prod_rows), 'rows')

    print()
    print('Exports complete. Files are in data/processed/')

if __name__ == '__main__':
    run()
