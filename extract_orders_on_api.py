from mongodb import MongoDBManager
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

class ExtractOrderGmail:
    def __init__(self):
        db_name = 'stock_kabu'
        db = MongoDBManager(db_name, 'orders')
        self.df = db.convert_pandas()
        self._format_df()
        
    def _format_df(self):
        new_df = self.df[[]]
        