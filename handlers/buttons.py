from aiogram import Router, F, types
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from datetime import date
import pandas as pd


from handlers.commands import format_df_as_table
from database import create_transactions_table, connecting_to_db, create_categories_table, get_all_from_db
from keyboards import transaction_type_kb, category_selection_kb, main_menu_button_kb, cancel_kb


router = Router()


# Create class of transaction states
class TransactionAmount(StatesGroup):
    amount = State()
    category = State()
    transaction_type = State()




# Main menu button handler
@router.callback_query(F.data == 'cancel_and_return_to_main')
async def main_menu(callback: types.CallbackQuery):
     # Create tables if not exists
    await create_transactions_table()
    await create_categories_table(user_id=callback.from_user.id)
    # Send greeting message
    await callback.message.edit_text(
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


 
    
# Add expense/income button handler
@router.callback_query(F.data == 'add_button')
async def add_expense_income(callback: types.CallbackQuery):
    # Ask user to choose transaction type
    await callback.message.edit_text(
        f'Select transaction type:',
        reply_markup=transaction_type_kb()
    )
    
    
    
    
# Income/expense button handler
@router.callback_query(F.data.in_(['income', 'expense']))
async def select_transaction_type(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    # Set state to catch the transaction type
    await state.set_state(TransactionAmount.transaction_type)
    # Update state data
    await state.update_data(trans_type=callback.data)
    # Get categories data from the database
    async with connecting_to_db() as conn:
        c = conn.cursor()
        c.execute('''
                    SELECT income_categories, expense_categories
                    FROM categories
                    WHERE user_id = ?
                    ''', (user_id, ))
        result = c.fetchall()
        # Check which transaction type was selected
        categories_list = []
        if callback.data == 'income':
            # Add income categories to the list
            [categories_list.append(a) for (a, b) in result if a != None]
        else: # Add expense categories to the list
            [categories_list.append(b) for (a, b) in result if b != None]
    # Ask user to choose income category
    await callback.message.edit_text(
        'Please select a transaction category. \n'
        'If you don\'t see your desired category, press the <b>\'ADD CATEGORY\'</b> button to create a new one. \n'
        'To return to the main menu, press the <b>\'CANCEL\'</b> button.',
        reply_markup=category_selection_kb(categories_list=categories_list, callback_data=callback.data)
    )




# Category buttons handler
@router.callback_query(F.data.startswith('cat_'))
async def category_selection(callback: types.CallbackQuery, state: FSMContext):
    # Get category name from callback data
    cat_name = callback.data.replace('cat_', '').capitalize()
    # Set state to catch 'Transaction amount'
    await state.set_state(TransactionAmount.amount)
    # Inform user about the selected category
    msg = await callback.message.edit_text(
        f'Selected category is <b>{cat_name}</b>'
        f'\nEnter transaction amount:' # Ask user to enter the transaction amount
    )
    # Update state data 
    await state.update_data(category=cat_name, msg_id=msg)

    
    
    
    
# Transaction amount state handling    
@router.message(TransactionAmount.amount)
async def get_amount_state(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Update state data 
    await state.update_data(trans_am=message.text)
    # Get transaction data from the state
    data = await state.get_data()
    amount = data['trans_am']
    cat = data['category']
    trans_type = data['trans_type']
    msg_id = data['msg_id']
    
    # Delete preious message
    await msg_id.delete()
    
    # Get balance data from the database
    balance = await get_all_from_db(user_id=user_id, columns=['balance'])
    try:
        # Check if amount is an appropriate number type
        amount = float(data['trans_am'])
    except:
        # Ask user to enter appropriate number 
        await message.answer(
            'Please send the number without any characters in format <b>123.45</b> or <b>123</b>',
            )
            
    # Set balance data
    if trans_type == 'income': # Lower case because it was taken from the callback data
        balance += amount
    else:
        balance -= amount
    # Add transaction data into database
    async with connecting_to_db() as conn:
        c = conn.cursor()
        c.execute('''
                  INSERT INTO transactions (user_id, transaction_type, category, amount, balance, date)
                  VALUES (?, ?, ?, ?, ?, ?)
                  ''', 
                  (user_id, str(trans_type).capitalize(), cat, amount, balance, str(date.today()))
                  )  
        conn.commit()
    # Inform the user about the successful addition of the transaction
    await message.answer(
        f'Transaction has been added for <b>{str(cat).capitalize()}</b> category',
        reply_markup=main_menu_button_kb()
    )
    await state.clear()
        
        

# See data as DataFrame
@router.callback_query(F.data == 'show_dataframe')
async def show_data_as_df(callback: types.CallbackQuery):
    # Get data from databese according to user_id
    user_id = callback.from_user.id
    # Create DataFrame
    df = await get_all_from_db(
        user_id=user_id,
        as_dataframe=True,
        for_table=True,
        columns=['transaction_type', 'category', 'amount', 'balance', 'date']
        )
    # Rename column
    df['Type'] = df['Transaction Type']
    # Format datetype
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    df = df[['Type', 'Category', 'Amount', 'Balance', 'Date']]
    # Format manually DataFrame as a Markdown table
    try:
        formatted_table = await format_df_as_table(df)
    except Exception as e:
        print(f'Error occurred: {str(e)}') 
        await callback.answer('No data found, please add your first transaction', show_alert=True)
        return
    
    # Send the formatted table
    await callback.message.answer(f'```\n{formatted_table}\n```', parse_mode='Markdown', reply_markup=cancel_kb())