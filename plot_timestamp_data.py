import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mc
from datetime import timedelta
import ipywidgets as widgets
from ipywidgets import interact
from utility import handle_exception
import pdb

# ! test/ficture 内のものとほぼ同じ
def plot_draw_obj(draw_obj, args, add_obj_list):
        plt.figure(figsize=(20,8))
        draw_obj
        plt.show()



class GetPlotObjTimeStamp:
    def __init__(self, main_df, other_data_list=None):
        # other_data_listの各data  [x,y, args]
        self.main_df = main_df
        self.other_data_list = other_data_list
        self.main_subset_df = None
        self.other_subset_list = []
        #self.args = self._get_args()
        
    def get_plot(self,start_time, end_time):
        mask_main = (self.main_df.index >= start_time) & (self.main_df.index <= end_time)
        self.main_subset_df = self.main_df.loc[mask_main]
        
        fig, ax = plt.subplots(figsize=(25, 10))
        ax.plot(self.main_subset_df.index, self.main_subset_df['price'], marker='o', label='Price')

        # other draw_list の期間を変更
        if self.other_data_list:
            # other_data_listの各data  [x,y, args]
            try:
                for other_data in self.other_data_list:
                    x,y,args = other_data
                    ax.scatter(x, y, **args)
                    for i, (xi, yi) in enumerate(zip(x, y)):
                        ax.text(xi, yi, f' {i}', color='red', fontsize=9, ha='left', va='center')
            except:
                handle_exception()
                raise      
        plt.legend()
        plt.show()
        
    def continuous_display_within_period(self, start_time_end_time, interval):
        pass
    
        
        
if __name__ == '__main__':
    df = pd.DataFrame({
    '約定単価': [100, 200, 300, 400, 500],
    '日付': pd.date_range(start='2024-06-01', periods=5, freq='D')
    })
    df.set_index('日付', inplace=True)

    # クラスのインスタンスを作成してプロットを行う
    plotter = GetPlotObjTimeStamp(df)
    plotter.get_period(pd.Timestamp('2024-06-02'), pd.Timestamp('2024-06-04')) 
    

