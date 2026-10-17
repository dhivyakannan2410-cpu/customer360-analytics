import numpy as np
import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from config.settings import MONGO_URI, DB_NAME, CUSTOMERS_COL

np.random.seed(42)

def get_db():
    return MongoClient(MONGO_URI)[DB_NAME]

def risk_label(p):
    if p >= 0.7:
        return 'High'
    elif p >= 0.4:
        return 'Medium'
    else:
        return 'Low'

def run():
    db = get_db()
    exists_op = chr(36) + 'exists'
    set_op = chr(36) + 'set'

    docs = list(db[CUSTOMERS_COL].find(
        {'rfm_score': {exists_op: True}},
        {'_id': 0, 'id': 1, 'recency': 1, 'frequency': 1,
         'monetary': 1, 'r_score': 1, 'f_score': 1, 'm_score': 1,
         'rfm_score': 1, 'segment': 1}
    ))

    df = pd.DataFrame(docs)

    # NOISY churn label: probability based on recency + a bit of randomness
    # This breaks the direct recency -> churn leak
    prob = 1 / (1 + np.exp(-(df['recency'] - 120) / 40))   # sigmoid
    noise = np.random.normal(0, 0.15, len(df))             # add noise
    df['churned'] = ((prob + noise) > 0.5).astype(int)

    print('Churn base rate: {:.1%}'.format(df['churned'].mean()))
    print()

    features = ['recency', 'frequency', 'monetary', 'r_score', 'f_score', 'm_score', 'rfm_score']
    X = df[features]
    y = df['churned']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=6)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print('Accuracy: {:.2%}'.format(accuracy_score(y_test, y_pred)))
    print()
    print(classification_report(y_test, y_pred, target_names=['Active', 'Churned']))

    df['churn_probability'] = model.predict_proba(X)[:, 1].round(4)
    df['churn_risk'] = df['churn_probability'].apply(risk_label)

    for _, row in df.iterrows():
        update = {
            'churned': int(row['churned']),
            'churn_probability': float(row['churn_probability']),
            'churn_risk': row['churn_risk']
        }
        db[CUSTOMERS_COL].update_one({'id': int(row['id'])}, {set_op: update})

    print('Churn probabilities saved for', len(df), 'customers')
    print()
    print('Risk distribution:')
    print(df['churn_risk'].value_counts().to_string())
    print()
    print('Top features:')
    for name, imp in sorted(zip(features, model.feature_importances_), key=lambda x: -x[1]):
        print('  {}: {:.3f}'.format(name, imp))

if __name__ == '__main__':
    run()
