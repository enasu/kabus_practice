from mongodb import MongoDBManager
from test.check_mongo_ticks import check_data_type_on_mongo_ticks
from plot_step_val import PlotStepValue, GetDFFromTicksjson
from ticks_handling import fetch_ticks_after_treatment

def fetch_unique_field():
    db_name = 'stock_kabu'
    db = MongoDBManager(db_name, 'orders_on_gmail')
    db.fetch_unique_field()   
    


if __name__=='__main__':

    #check_data_type_on_mongo_ticks()
    motodf=GetDFFromTicksjson()