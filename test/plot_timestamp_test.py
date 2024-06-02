from plot_timestamp_data import GetPlotObjTimeStamp
from extract_orders_on_gmail import ExtractOrderGmail
from ticks_handle import TicksExtractHandler
import pandas as pd


def get_plot_object_timestamp_simple():
    df = pd.DataFrame({
    '約定単価': [100, 200, 300, 400, 500],
    '日付': pd.date_range(start='2024-06-01', periods=5, freq='D')
    })
    df.set_index('日付', inplace=True)

    # クラスのインスタンスを作成してプロットを行う
    plotter = GetPlotObjTimeStamp(df)
    plotter.get_period(pd.Timestamp('2024-06-02'), pd.Timestamp('2024-06-04')) 
    

def get_plot_object_timestamp():
    code=9509
    ticks_obj = TicksExtractHandler()
    ticks_obj.exec(str(code))
    ticks_df = ticks_obj.df
    
    start_time = pd.to_datetime('2024-05-30 09:00:00.000000')
    end_time = pd.to_datetime('2024-05-30 15:00:00.000000')
    gmail_obj = ExtractOrderGmail()
    other_draw_data_list = gmail_obj.get_other_data_list(code, start_time, end_time, plot_lib="matplot")
    
    plot_obj = GetPlotObjTimeStamp(ticks_df, other_draw_data_list)
    plot_obj.get_plot(start_time, end_time)

def test_continuous_display_simple():
    # データフレームの例
    dates = pd.date_range('20230101', periods=100)
    data = pd.DataFrame(data={'price': range(100)}, index=dates)

    # インスタンス化とメソッドの呼び出し
    plot_obj = GetPlotObjTimeStamp(main_df=data)
    plot_obj.continuous_display_within_period(dates[0], dates[-1], pd.Timedelta(days=10))
    
class TestPlotObjTimestamp:
    def __init__(self):
        code=9509
        ticks_obj = TicksExtractHandler()
        ticks_obj.exec(str(code))
        self.start_time = pd.to_datetime('2024-05-30 09:00:00.000000')
        self.end_time = pd.to_datetime('2024-05-30 15:00:00.000000')
        self.gmail_obj = ExtractOrderGmail()
        other_draw_data_list = self.gmail_obj.get_other_data_list(code, self.start_time, self.end_time, plot_lib="matplot")
        self.plot_obj = GetPlotObjTimeStamp(ticks_obj.df, other_draw_data_list)
        
    def test_get_plot(self):

        self.plot_obj.get_plot(self.start_time, self.end_time)
      
    def test_continuous_display(self):
        interval = pd.Timedelta(minutes=60)
        self.plot_obj.continuous_display_within_period(self.start_time, self.end_time, interval)
    

if __name__ == '__main__':
    #get_plot_object_timestamp_simple()
    #get_plot_object_timestamp()
    #test_continuous_display_simple()
    plot_obj = TestPlotObjTimestamp()
    plot_obj.test_get_plot()
    plot_obj.test_continuous_display()