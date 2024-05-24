from utility import date_to_microsecond, datetime_to_unixtime, DateTimeParser


datetime_list=["20240522", "2024/05/22", "2024/05/22 15:10:00", 
               "20240522 15:10:00"]

def measure_len():
    c=0
    for datetime in datetime_list:
        c=c+1 
        print(f'measure_len {c}>>> {datetime} : {len(datetime)}')

def test_date_to_microsecond():
    c=0
    try:
        for datetime in datetime_list:
            c=c+1
            print(f'test_deate_to_microsecond {c}>>> {datetime} : {date_to_microsecond(datetime)}')    
    except Exception as e:
        print(e)
    
# def test_deatetime_to_unixtime():
#     c=0
#     for datetime in datetime_list:
#         c=c+1
#         print(f'test_deatetime_to_unixtime {c}>>> {datetime} : {datetime_to_unixtime(datetime)}')
        
       
def test_datetimeparser():
    c=0
    for datetime in datetime_list:
        c=c+1
        parser = DateTimeParser(datetime)
        print(f'test_DateTimeParser {c}>>> {datetime} : unix time: {parser.unix_time}')
        print(f'                                      : microsec : {parser.microsec}')

if __name__ == '__main__':
    measure_len()
    test_date_to_microsecond()
    #test_deatetime_to_unixtime()
    test_datetimeparser()
        
