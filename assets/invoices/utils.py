# utils.py

def get_company_from_user(user):
    try:
        if hasattr(user, 'company') and user.company:
            return user.company
        if hasattr(user, 'employee_account') and user.employee_account.company:
            return user.employee_account.company
    except Exception:
        pass
    return None
