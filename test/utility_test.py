from utility import DateTimeParser


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
        print(f'test_DateTimeParser {c}>>> {datetime} : unix time: {parser.unix_time}')
        print(f'                                      : microsec : {parser.microsec}')

if __name__ == '__main__':
    measure_len()
    test_datetimeparser()
        
