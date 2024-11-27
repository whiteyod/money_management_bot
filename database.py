import contextlib
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import pandas as pd
import sqlite3






# Set up default categories
expense_categories = [
    'Grocery', 'Transport', 'Medical', 'Personal', 'Family', 'Home', 'Car', 'Dining', 'Subsriptions'
]
income_categories = [
    'Salary', 'Presents', 'Bussines income', 'Loans', 'Interest returnings'
]




# Connecting to database
@contextlib.asynccontextmanager
async def connecting_to_db():
    conn = sqlite3.connect('transactions_and_cats.db')
    try:
        yield conn
    finally:
        conn.close()




# Create the table for transactions
async def create_transactions_table():
    ''' Creates table with user transactions data in existing database
        
    Args:
        None.

    Returns:
        Message indicating successful table creation.'''
    try:
        async with connecting_to_db() as conn:
            c = conn.cursor()
            c.execute('''
                      CREATE TABLE IF NOT EXISTS transactions
                      ([id] INTEGER PRIMARY KEY AUTOINCREMENT,
                      [user_id] INTEGER,
                      [transaction_type] TEXT,
                      [category] TEXT,
                      [amount] FLOAT,
                      [balance] FLOAT,
                      [date] TEXT
                      )''')
        return print('Table Transactions was created successfully.')
    except Exception as e:
        print(f'An error occurred: {e}')
        return print('Failed to create transactions table.')
    
    
    

# Create table for user-defined categories
async def create_categories_table(user_id):
    ''' Creates table with user-defined categories data in existing database
        
    Args:
        user_id (int): Unique user ID from Telegram.

    Returns:
        Message indicating successful table creation.'''
    try:
        async with connecting_to_db() as conn:
            c = conn.cursor()
            c.execute('''
                      CREATE TABLE IF NOT EXISTS categories
                      ([id] INTEGER PRIMARY KEY AUTOINCREMENT,
                      [user_id] INTEGER,
                      [expense_categories] TEXT,
                      [income_categories] TEXT
                      )
                      ''')
            # Insert default expense categories if not already present
            for cat in expense_categories:
                c.execute('''
                          INSERT OR IGNORE INTO categories (user_id, expense_categories)
                          SELECT ?, ?
                          WHERE NOT EXISTS (
                              SELECT 1 FROM categories
                              WHERE user_id = ? AND expense_categories = ?
                          )
                          ''', (user_id, cat, user_id, cat))
            
            # Insert default income categories if not already present
            for cat in income_categories:
                c.execute('''
                          INSERT OR IGNORE INTO categories (user_id, income_categories)
                          SELECT ?, ?
                          WHERE NOT EXISTS (
                              SELECT 1 FROM categories
                              WHERE user_id = ? AND income_categories = ?
                          )
                          ''', (user_id, cat, user_id, cat))
            conn.commit()
        return print('Table Categories was created successfully.')
    except Exception as e:
        print(f'An error occurred: {e}')
        return print('Failed to create Categories table.')
    
    


# Get all the data from the transaction table
async def get_all_from_db(user_id, as_dataframe=False, get_all=False, for_table=False, **kwargs):
    ''' Gets all or choosen one columns with the transactions data from the database
    
    Args:
        user_id (int): Unique user ID from Telegram.
        
        as_dataframe (bool): Optional, False by default, if True returns data as DataFrame.
        
        get_all (bool): Optional, False by default, if True returns all available columns. 
        
        for_table (bool): Optional, False by default, if True returns data of all rows.
        
        kwargs (list): Columns to select from the database.
        

    Returns:
        Selected columns with the transaction data as a DataFrame for specific user from the database.
        Or
        Selected columns with the transaction data as a list of tuples.'''
        
    # Columns selection
    if get_all:
        columns = ['transaction_type', 'category', 'amount', 'balance', 'date']
    else:
        columns = kwargs.get('columns', ['transaction_type', 'category', 'amount', 'balance', 'date'])
    # Convert columns to the string
    columns_str = ', '.join(columns)
        
    # Convert data if balance column is selected
    if columns == ['balance']:
        async with connecting_to_db() as conn:
            c = conn.cursor()
            c.execute('''
                      SELECT balance 
                      FROM transactions
                      WHERE user_id = ? 
                      ORDER BY id DESC LIMIT 1
                      ''',
                      (user_id,))
            # Select the last balance record
            balance = c.fetchone()
        # If no previous records set default value
        if balance is None:
            balance = 0
        else: # Convert tuple into float    
            balance = float(balance[0])
        results = balance
    else: # Get all the results if other columns is selected
        
        # Get current date
        current_date = datetime.today().date()
        # Get number of the month day
        day_num = current_date.strftime('%d')
        # Get first day of the month
        start_date = current_date - timedelta(days=int(day_num) - 1)
        # Get last day of the month
        end_date = current_date + relativedelta(day=31)
        async with connecting_to_db() as conn:
            c = conn.cursor()
            if for_table == True:
                c.execute(f'''
                        SELECT {columns_str}
                        FROM transactions
                        WHERE user_id = ?
                        ''',
                        (user_id, ))
            else:
                c.execute(f'''
                        SELECT {columns_str}
                        FROM transactions
                        WHERE user_id = ? AND date BETWEEN ? AND ?
                        ''',
                        (user_id, start_date, end_date,))
            results = c.fetchall()
    if as_dataframe:
        # Create DataFrame
        df = pd.DataFrame(results, columns=['Transaction Type', 'Category', 'Amount', 'Balance', 'Date'])
        df['Date'] = pd.to_datetime(df['Date'])
        # Return df in descending order
        return df.sort_index(ascending=False)
    else:
        # Return data as a list of tuples
        return results