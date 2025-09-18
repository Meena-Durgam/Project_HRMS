def is_hr_user(user):
    try:
        # Check if the user is a company owner (assuming role is a string field)
        if getattr(user, 'role', '').strip().lower() == 'company_owner':
            return True

        # Check if user is an HR employee
        employee = user.employee_account  # One-to-one relation from CustomUser to Employee
        return (
            employee.department and
            employee.department.name.strip().lower() == "human resources"
        )
    except Exception:
        return False
