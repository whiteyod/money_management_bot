from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from datetime import datetime
import pandas as pd
from requests import Session

from keyboards import main_menu_button_kb
from database import create_categories_table, create_transactions_table, connecting_to_db, get_all_from_db


router = Router()


# Start command handler
@router.message(Command('start'))
async def cmd_start(message: Message):
    # Create tables if not exists
    await create_transactions_table()
    await create_categories_table(user_id=message.from_user.id)
    # Send greeting message
    await message.answer(
        '<b>Money Management Bot Main Menu</b>\n\n'
        'Welcome to the Money Management Bot! Please select an option from the menu below:\n\n'
        '1. <b>Add Transaction</b> - Add a new transaction to track your expenses or income.\n'
        '2. <b>View Transactions</b> - View your transaction history.\n'
        '3. <b>Edit Transaction</b> - Modify an existing transaction.\n'
        '4. <b>Delete Transaction</b> - Remove a transaction from your history.\n'
        '5. <b>Set Budget</b> - Set or update your budget for better expense management.\n'
        '6. <b>View Budget</b> - Check your current budget and progress.\n'
        '7. <b>Statistics</b> - Get an overview of your financial statistics.\n'
        '8. <b>Help</b> - Get help and information about using the bot.\n\n'
        'Please type the number corresponding to the option you want to choose, or use the buttons below.',
        reply_markup=main_menu_button_kb()
    )
    
    
    
    
# Test command handler 
@router.message(Command('test'))
async def cmd_test(message: Message):
    user_id = message.from_user.id
    async with connecting_to_db() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM categories WHERE user_id = ?", (user_id,))
        print(c.fetchall())
    
    
    
    
    
    
# Function to manually format the DataFrame as a fixed-width text table
async def format_df_as_table(df):
    """
    Formats a pandas DataFrame as a fixed-width text table.

    Parameters:
        df (pandas.DataFrame): The DataFrame to be formatted.

    Returns:
        str: A string representation of the DataFrame in a fixed-width text table format.
    """
    # Define column widths
    col_widths = [max(df[col].astype(str).map(len).max(), len(col)) for col in df.columns]
    lines = []

    # Header
    header = " | ".join(f"{col:<{col_widths[i]}}" for i, col in enumerate(df.columns))
    lines.append(header)
    lines.append("-|-".join("-" * col_width for col_width in col_widths))

    # Rows
    for _, row in df.iterrows():
        line = " | ".join(f"{str(row[col]):<{col_widths[i]}}" for i, col in enumerate(df.columns))
        lines.append(line)

    return "\n".join(lines)