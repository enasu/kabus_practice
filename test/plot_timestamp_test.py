from plot_timestamp_data import GetPlotObjTimeStamp
import pandas as pd


def test_continuous_display():
    # データフレームの例
    dates = pd.date_range('20230101', periods=100)
    data = pd.DataFrame(data={'price': range(100)}, index=dates)

    # インスタンス化とメソッドの呼び出し
    plot_obj = GetPlotObjTimeStamp(main_df=data)
    plot_obj.continuous_display_within_period(dates[0], dates[-1], pd.Timedelta(days=10))
    

if __name__ == '__main__':
    test_continuous_display()