from aiogram import Router, F, types
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from datetime import date
import pandas as pd

from database import connecting_to_db
from keyboards import transaction_type_kb, category_selection_kb, main_menu_button_kb, cancel_kb

router = Router()


# Create class of new category state
class NewCategory(StatesGroup):
    category_type = State()
    category_name = State()




# Add new user-defined category for expenses
@router.callback_query(F.data.in_(['add_expense_cat', 'add_income_cat']))
async def add_user_defined_category(callback: types.CallbackQuery, state: FSMContext):
    category_type = 'expense' if callback.data == 'add_expense_cat' else 'income'
    # Clear previous state to avoid errors
    await state.clear()
    # Set new state to catch category type
    await state.update_data(category_type=category_type)
    # Set new state to catch category name
    await state.set_state(NewCategory.category_name)
    # Ask user to enter name for the new category
    await callback.message.answer('Enter new category name: ', reply_markup=cancel_kb())
    
    
        
    
# New expense category state handling
@router.message(NewCategory.category_name)
async def new_expense_category_handling(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Get data from the state
    data = await state.get_data()
    category_type = data['category_type']
    new_cat_name = message.text
    # Add categories data in the database
    with connecting_to_db() as conn:
        c = conn.cursor()
        if category_type == 'expense':
            c.execute('''
                    INSERT OR IGNORE INTO categories (user_id, expense_categories)
                    VALUES (?, ?)
                    ''',
                    (user_id, new_cat_name))
        else:
            c.execute('''
                      INSERT OR IGNORE INTO categories (user_id, income_categories)
                      VALUES (?, ?)
                      ''', (user_id, new_cat_name))
        conn.commit()
    await message.answer(
        f'<b>{new_cat_name}</b> category for <b>{str(category_type).capitalize()}</b> has been added!',
        reply_markup=main_menu_button_kb()
        )
    await state.clear()