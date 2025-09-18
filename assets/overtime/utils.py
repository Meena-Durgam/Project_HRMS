# overtime/utils.py or common/utils.py

def is_hr_user(user):
    return (
        hasattr(user, 'employee_account') and
        user.employee_account.department and
        user.employee_account.department.name.lower() == 'human resources'
    )
