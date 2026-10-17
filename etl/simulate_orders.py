import random
from datetime import datetime, timedelta
from faker import Faker
from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME

fake = Faker()
random.seed(42)

def get_db():
    return MongoClient(MONGO_URI)[DB_NAME]

def run():
    db = get_db()
    customers = list(db['customers'].find({}, {'_id': 0, 'id': 1}))
    products = list(db['products'].find({}, {'_id': 0, 'id': 1, 'title': 1, 'price': 1, 'category': 1}))

    if not customers or not products:
        print('Run etl/fetch_api.py first.')
        return

    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    orders = []
    order_id = 1000

    for cust in customers:
        # Each customer places 1 to 15 orders
        num_orders = random.randint(1, 15)
        for _ in range(num_orders):
            order_date = fake.date_time_between(start_date=start_date, end_date=end_date)
            num_items = random.randint(1, 4)
            items = random.sample(products, num_items)

            cart_products = []
            total = 0.0
            for p in items:
                qty = random.randint(1, 3)
                line_total = round(p['price'] * qty, 2)
                total += line_total
                cart_products.append({
                    'id': p['id'],
                    'title': p['title'],
                    'price': p['price'],
                    'quantity': qty,
                    'total': line_total
                })

            orders.append({
                'order_id': order_id,
                'customer_id': cust['id'],
                'products': cart_products,
                'total': round(total, 2),
                'total_products': len(cart_products),
                'total_quantity': sum(i['quantity'] for i in cart_products),
                'order_date': order_date,
                'status': random.choice(['Delivered']*7 + ['Shipped', 'Cancelled', 'Returned'])
            })
            order_id += 1

    db['orders'].drop()
    db['orders'].insert_many(orders)

    print('Created', len(orders), 'orders for', len(customers), 'customers')
    print('Avg orders per customer: {:.1f}'.format(len(orders)/len(customers)))

if __name__ == '__main__':
    run()
