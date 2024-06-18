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


class BasePlotObj:
    def __init__(self, main_df, other_data_list=None):
        self.main_df = main_df
        self.other_data_list = other_data_list
        self.title_str = None

    def get_time_filtered_data(self, start_time, end_time):
        mask_main = (self.main_df.index >= start_time) & (self.main_df.index <= end_time)
        return self.main_df.loc[mask_main]

    def plot(self, title_str, start_time, end_time):
        self.title_str = title_str
        raise NotImplementedError("This method should be implemented by subclasses.")

    def continuous_display_within_period(self, start_time, end_time, interval):
        # 指定された間隔で連続的にプロットを表示
        current_time = start_time
        while current_time < end_time:
            next_time = min(current_time + interval, end_time)
            self.plot(self.title_str, current_time, next_time)
            current_time += interval



class PlotTimeStamp(BasePlotObj):
        
    def plot(self, title_str, start_time, end_time):
        subset_df = self.get_time_filtered_data(start_time, end_time)
        addplotdatas =[]
        
        fig, ax = plt.subplots(figsize=(25, 10))
        ax.plot(subset_df.index, subset_df['price'], marker='o', label='Price')
        
        # # グラフのタイトルを設定
        title = f"{title_str}  {start_time}>>{end_time}"
        plt.title(title)  

        # other draw_list の期間を変更
        if self.other_data_list:
            # other_data_listの各data  [x,y, args]
            try:
                for other_data in self.other_data_list:
                    other_df, other_args = other_data
                    mask_other = (other_df.index >= start_time) & (other_df.index <= end_time)
                    other_sub_df = other_df.loc[mask_other] 
                    ax.scatter(other_sub_df.index, other_sub_df['price'], **other_args)
                    for i, (xi, yi) in enumerate(zip(other_sub_df.index, other_sub_df['price'])):
                        if 'exit' in other_args['label']:
                            ax.text(xi, yi, f' {i}:{other_sub_df.loc[xi, "pl"]}', color='red', fontsize=9, ha='center', va='bottom')
                        else:
                            ax.text(xi, yi, f' {i}', color='red', fontsize=9, ha='left', va='center')
                            
            except:
                handle_exception()
                raise      
        plt.legend()
        plt.show()
        
    # def continuous_display_within_period(self, code, start_time, end_time, interval):
    #     # 指定された間隔で連続的にプロットを表示
    #     current_time = start_time
    #     while current_time < end_time:
    #         next_time = min(current_time + interval, end_time)
    #         self.plot(str(code), current_time, next_time)
    #         current_time += interval
    
        

    

