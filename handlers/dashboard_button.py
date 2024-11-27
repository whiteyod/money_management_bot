from aiogram import Router, F, types
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from datetime import date
import pandas as pd

from database import connecting_to_db, get_all_from_db
from keyboards import transaction_type_kb, category_selection_kb, main_menu_button_kb, cancel_kb
from other_functions import get_month


router = Router()


@router.callback_query(F.data == 'show_dashboard')
async def show_dashboard_button(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    # Get data from the database as DataFrame
    try:
        df = await get_all_from_db(user_id=user_id, as_dataframe=True, get_all=True)
    except Exception as e:
        await print(f'Error occured: {str(e)}')
        return

    # # Subset DataFrame to get current month data
    # try:
    #     df = get_month(df)
    # except Exception as e:
    #     await print(f'Error occurred: {str(e)}')
    #     return

    # Sort transactions by category
    try:
        sorted_df = df.groupby(['Transaction Type', 'Category'])['Amount'].sum().reset_index()
    except Exception as e:
        print(f'Error occurred: {str(e)}')
        return

    # Get only expenses data and convert into 2D array
    try:
        expenses = sorted_df[sorted_df['Transaction Type'] == 'Expense'].values
    except Exception as e:
        print(f'Error occurred: {str(e)}')
        return

    # Get only incomes data and convert into 2D array
    try:
        incomes = sorted_df[sorted_df['Transaction Type'] == 'Income'].values
    except Exception as e:
        print(f'Error occurred: {str(e)}')
        return

    # Set dashboard info
    dashboard_info = [f'You spent this month: \n']
    for i in expenses: # Add expenses data
        if i is None:
            continue
        dashboard_info.append(f'<b>{i[1]}: {i[2]}</b>\n')
    dashboard_info.append(f'\nYou earn this month: \n')
    for i in incomes: # Add incomes data
        if i is None:
            continue
        dashboard_info.append(f'<b>{i[1]}: {i[2]}</b>\n')

    # Add balance data
    try:
        balance = df["Balance"].iloc[0]
    except Exception as e:
        await callback.answer(f'No data found, please add your first transaction', show_alert=True)
        return
    dashboard_info.append(f'\nCurrent balance: {balance}')
    edited_dashboard = '\n'.join(dashboard_info)
    # Show dashboard to the user
    await callback.message.edit_text(f'{edited_dashboard}', reply_markup=cancel_kb(text='Main menu'))

    
    