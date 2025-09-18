# accounts/middleware/check_company_and_employee_profile.py

from django.shortcuts import redirect
from django.contrib import messages

EXACT_EXEMPT_PATHS = [
    '/',  # Homepage
    '/accounts/login/',
    '/accounts/logout/',
    '/accounts/setup-company-profile/',
    '/employee/my-profile/',
    '/dashboard/employee/',
    '/dashboard/company/',
]

PREFIX_EXEMPT_PATHS = [
    '/admin/',
    '/static/',
    '/media/',
]

class CheckCompanyAndEmployeeProfileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        def is_exempt(path):
            return path in EXACT_EXEMPT_PATHS or any(path.startswith(p) for p in PREFIX_EXEMPT_PATHS)

        # ✅ Skip if unauthenticated or exempt
        if not request.user.is_authenticated or is_exempt(path):
            return self.get_response(request)

        # ✅ Company Owner check
        if request.user.role == 'company_owner':
            try:
                company = request.user.company
                if company and not company.complete_profile:
                    messages.warning(request, "Please complete your company profile to proceed.")
                    return redirect('/accounts/setup-company-profile/')
            except AttributeError:
                pass

        # ✅ Employee check
        if request.user.role == 'employee' and hasattr(request.user, 'employee_account'):
            employee = request.user.employee_account
            profile = getattr(employee, 'profile', None)

            if profile:
                profile.check_profile_completion()

                if not profile.is_completed or not profile.is_approved:
                    if not is_exempt(path):
                        messages.warning(request, "You must complete and get approval for your profile.")
                        return redirect('/employee/my-profile/')
            else:
                messages.warning(request, "Employee profile missing. Please contact admin.")
                return redirect('/employee/my-profile/')

        return self.get_response(request)
