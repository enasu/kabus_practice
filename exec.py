from mongodb import MongoDBManager

if __name__=='__main__':

    db_name = 'stock_kabu'
    db = MongoDBManager(db_name, 'orders_on_gmail')
    db.fetch_unique_field()