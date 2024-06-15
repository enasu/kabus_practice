from utility import DateTimeParser, PeriodFilterMaker
from datetime import timedelta, datetime, time
import pdb



datetime_list=["20240522", "2024/05/22", "2024/05/22 15:10:00", 
               "20240522 15:10:00"]

def measure_len():
    c=0
    for datetime in datetime_list:
        c=c+1 
        print(f'measure_len {c}>>> {datetime} : {len(datetime)}')
        
       
def test_datetimeparser():
    c=0
    for datetime in datetime_list:
        c=c+1
        parser = DateTimeParser(datetime)
        print(f'test_DateTimeParser {c}>>> {datetime} : date_std : {parser.date_std}')
        print(f'                                      : microsec : {parser.microsec}')
        print(f'                                      : unix time: {parser.unix_time}')
        previous_parser = parser.get_previous_day()
        print(f'前日は             : date_std : {previous_parser.date_std}')
        print(f'                   : microsec : {previous_parser.microsec}')
        print(f'                   : unix time: {previous_parser.unix_time}')
        
def test_priod_filtermaker():
    # 現在の日時を取得
    dt_now = datetime.now()
    today = datetime.combine(dt_now.date(), time.min)
    today_str = today.strftime('%Y%m%d')
    period_obj = PeriodFilterMaker()
    period_obj.oneday_period(today_str)
    print(f'一日の date_std fileter: {period_obj.date_std("日時")}')
    print(f'一日の date_micro fileter: {period_obj.date_micro("timestamp")}')
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')
    period_obj.between_date(yesterday_str, today_str)
    print(f'一日両日の date_std fileter: {period_obj.date_std("日時")}')
    print(f'一日両日の date_micro fileter: {period_obj.date_micro("timestamp")}')

if __name__ == '__main__':
    #measure_len()
    #test_datetimeparser()
    test_priod_filtermaker()
        
