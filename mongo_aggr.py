from pymongo import MongoClient

mongo = MongoClient("mongodb://localhost:27017/")
db = mongo["magnit"]

q = db.promo.aggregate([
    {
        '$group': {
            '_id': '$promo_name',
            'promo': {'$push': '$$ROOT'}
        }
    }
])

for x in q:
    print(x['_id'])
    print(('\n').join([itm['product_name'] for itm in x['promo']]))
    print('\n')
