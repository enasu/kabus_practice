from extract_orders_on_gmail import ExtractOrderGmail, get_contract_df
from fixture import fixture_date_set
from datetime import datetime as dt
import datetime
import pdb
import pprint

def test_extract_order_on_gmail(code, entry_date, exit_date):
    gmail_obj = ExtractOrderGmail()
    gmail_df = gmail_obj.df
    print(f'-----------------gmail_df -----------------')
    print(gmail_df.head(2))
    
    entry_time = dt.combine(entry_date, datetime.time(8,59,0))
    exit_time = dt.combine(exit_date, datetime.time(15,1,0))
    
    print(f' gmail_df の indexの type :{type(gmail_df.index)} ')
    print(f'entry_time  {entry_time} のtype : {type(entry_time)}')

    # f_df =  gmail_df[(gmail_df.index >= entry_time) & (gmail_df.index <= exit_time) \
    #      & (gmail_df['銘柄CD']==str(code)) ]
    # print(f'-----------------f_df -----------------')
    # print(f_df.head(2))
    
    dict_list = get_contract_df(code, entry_time, exit_time)
        
    #print(dict_list)
    
    # plot_testに利用する
    return dict_list
    
    



if __name__ == '__main__':
    setups = fixture_date_set()
    setup_dates = setups[1].get('usedate')
    pprint.pprint(f'  setup_times  >>> {setup_dates}')
    entry_date = setup_dates[0]
    exit_date = setup_dates[1]
    
    code =9509
    test_extract_order_on_gmail(code, entry_date,entry_date)