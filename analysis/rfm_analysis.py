import pandas as pd
from datetime import datetime
from pymongo import MongoClient
from config.settings import MONGO_URI, DB_NAME, CUSTOMERS_COL

def get_db():
    return MongoClient(MONGO_URI)[DB_NAME]

def segment_customer(row):
    score = row['rfm_score']
    r, f = row['r_score'], row['f_score']
    if score >= 13 and r >= 4 and f >= 4:
        return 'Champion'
    elif score >= 10:
        return 'Loyal'
    elif score >= 7:
        return 'At Risk'
    else:
        return 'Lost'

def run():
    db = get_db()
    orders = list(db['orders'].find({}, {'_id': 0}))
    if not orders:
        print('No orders found.')
        return

    df = pd.DataFrame(orders)
    df['order_date'] = pd.to_datetime(df['order_date'])

    snapshot = df['order_date'].max() + pd.Timedelta(days=1)

    rfm = df.groupby('customer_id').agg(
        recency=('order_date', lambda x: (snapshot - x.max()).days),
        frequency=('order_id', 'count'),
        monetary=('total', 'sum')
    ).reset_index()

    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1]).astype(int)
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)
    rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5]).astype(int)
    rfm['rfm_score'] = rfm['r_score'] + rfm['f_score'] + rfm['m_score']
    rfm['segment'] = rfm.apply(segment_customer, axis=1)

    set_op = chr(36) + 'set'

    for _, row in rfm.iterrows():
        update = {
            'recency': int(row['recency']),
            'frequency': int(row['frequency']),
            'monetary': float(row['monetary']),
            'r_score': int(row['r_score']),
            'f_score': int(row['f_score']),
            'm_score': int(row['m_score']),
            'rfm_score': int(row['rfm_score']),
            'segment': row['segment']
        }
        db[CUSTOMERS_COL].update_one(
            {'id': int(row['customer_id'])},
            {set_op: update}
        )

    print('RFM updated for', len(rfm), 'customers')
    print()
    print('Segment distribution:')
    print(rfm['segment'].value_counts().to_string())

if __name__ == '__main__':
    run()
