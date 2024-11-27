from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types




# Add new transaction
def main_menu_button_kb():
    kb = InlineKeyboardBuilder()
    kb.add(
        types.InlineKeyboardButton(
            text='Add Transaction',
            callback_data='add_button'
        ),
        types.InlineKeyboardButton(
            text='View Transactions',
            callback_data='show_dataframe'
        ),
        types.InlineKeyboardButton(
            text='Dashboard',
            callback_data='show_dashboard'
        )
    )
    kb.adjust(2)
    return kb.as_markup()


# Select transaction type
def transaction_type_kb():
    kb = InlineKeyboardBuilder()
    kb.add(
        types.InlineKeyboardButton(
            text='Expense',
            callback_data='expense'
        ),
        types.InlineKeyboardButton(
            text='Income',
            callback_data='income'
        )
    )
    return kb.as_markup()


# Expense/income category selection
def category_selection_kb(categories_list: list, callback_data: str):
    if callback_data == 'income':
        add_button_callback = 'add_income_cat'
    elif callback_data == 'expense':
        add_button_callback = 'add_expense_cat'
    kb = InlineKeyboardBuilder()
    for category in categories_list:
        kb.add(
            types.InlineKeyboardButton(
                text=category.capitalize(),
                callback_data='cat_' + category.lower()
            )
    )
    kb.add(
        types.InlineKeyboardButton(
            text='CANCEL',
            callback_data='cancel_and_return_to_main'
        ),
        types.InlineKeyboardButton(
            text='ADD CATEGORY',
            callback_data=add_button_callback
        )
    )
    kb.adjust(2)
    return kb.as_markup()


# Return to main menu
def cancel_kb(text='Cancel'):
    kb = InlineKeyboardBuilder().add(
        types.InlineKeyboardButton(
            text=text,
            callback_data='cancel_and_return_to_main'
        )
    )
    return kb.as_markup()