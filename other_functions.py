from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import pandas as pd


# Subset data by date
def get_month(df):
    ''' Subsets data from the DataFrame for specific date range <b>(current month by default)</b>.
    
    Args:
        df(dataframe): DataFrame with the user data.
    
    Returns:
        DataFrame with the data selected for specific month.
    '''
    # Get current data
    current_date = datetime.today().date()

    # Get number of the month day
    day_num = current_date.strftime('%d')
    # Get first day of the month
    start_date = current_date - timedelta(days=int(day_num) - 1)
    
    # Get last day of the month
    end_date = current_date + relativedelta(day=31)
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Subset date  
    df = df[(df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))]
    
    return df

# df = pd.read_csv('lolkek.csv')
# get_month(df)