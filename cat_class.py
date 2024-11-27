from database import income_categories, expense_categories


# Define expense category class
class ExpenseCategory:
    all_categories = []
    all_budgets = []
    
    def __init__(self, name, budget) -> None:
        self.name = name
        self.budget = budget
        self.callback_data = name.lower() + '_cat'
        ExpenseCategory.all_categories.append(self.name)
        


cat = ExpenseCategory('Food', 150)
print('Category name: ', cat.name, 'cat budget: ', cat.budget)
    


 