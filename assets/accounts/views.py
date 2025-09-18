from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import CompanyOwnerSignupForm, CompanySettingsForm
from .models import Company


def company_signup(request):
    """
    Handles company owner registration.
    Creates user and an empty company linked to that user.
    """
    if request.method == 'POST':
        form = CompanyOwnerSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'company_owner'
            user.save()

            # Create an empty company instance for the user
            company = Company.objects.create(email=user.email)
            user.company = company
            user.save()

            login(request, user)
            return redirect('setup_company_profile')
    else:
        form = CompanyOwnerSignupForm()

    # Always define password help texts regardless of GET or POST
    password_help_texts = form.get_password_help_texts()

    return render(request, 'accounts/signup.html', {
        'form': form,
        'password_help_texts': password_help_texts
    })


from employee.models import EmployeeProfile  # ✅ Make sure this is the correct import

def user_login(request):
    """
    Handles login logic with redirection based on user roles.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)

            # Role-based redirection
            if user.role == 'company_owner':
                if not user.company or not user.company.name:
                    return redirect('setup_company_profile')
                return redirect('company_owner_dashboard')

            elif user.role == 'employee':
                # ✅ Important: check profile status before dashboard access
                return redirect('employee_dashboard')  

            elif user.role == 'jobseeker':
                return redirect('jobseeker_dashboard')

            elif user.role == 'superadmin':
                return redirect('superadmin_dashboard')

        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'accounts/login.html')

# accounts/views.py
from .models import CustomUser
from django.http import JsonResponse

@login_required
def check_email(request):
    email = request.GET.get('email', '').strip()
    exists = CustomUser.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})

from employee.models import EmployeeProfile

@login_required
def employee_post_login(request):
    if request.user.role != 'employee':
        messages.error(request, "Unauthorized Access.")
        return redirect('home')

    employee = request.user.employee_account
    profile = getattr(employee, 'profile', None)

    if profile:
        profile.check_profile_completion()

        if not profile.is_completed:
            messages.warning(request, "Please complete your employee profile.")
            return redirect('employee_profile')
        elif not profile.is_approved:
            messages.warning(request, "Your Profile Is Pending Approval.")
            return redirect('employee_profile')
        else:
            return redirect('employee_dashboard')
    else:
        messages.error(request, "Profile not found. please Contact admin.")
        return redirect('home')

@login_required
def user_logout(request):
    """
    Logs out the current user, clears all sessions, and redirects to login.
    """
    # ✅ Log out user (clears auth session)
    logout(request)

    # ✅ Flush any remaining session data
    request.session.flush()

    # ✅ Add success message
    messages.success(request, "You have been logged out successfully.")

    return redirect('login')


@login_required
def setup_company_profile(request):
    """
    Allows company owner to set up their company profile.
    Redirects to dashboard if profile is already completed.
    """
    if request.user.role != 'company_owner':
        return redirect('user_login')

    company = request.user.company

    # ✅ Redirect if profile is already complete
    if company and company.name:
        return redirect('company_owner_dashboard')

    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            company = form.save()

            # ✅ Sync user fields with company info
            user = request.user
            user.email = company.email  # Optional sync
            user.first_name = company.name  # Save company name as first_name
            user.save()

            messages.success(request, "Company profile updated successfully.")
            return redirect('company_owner_dashboard')
    else:
        form = CompanySettingsForm(instance=company)

    return render(request, 'accounts/company_profile_setup.html', {'form': form})
from projects.models import Project
@login_required
def company_profile_view(request):   
    try:
        # Fetch company based on email or foreign key to user
        company = Company.objects.get(email=request.user.email)
        projects = Project.objects.filter(company=company)
    except Company.DoesNotExist:
        messages.error(request, "Company Profile Not Found.")
        return redirect('home')  # Replace 'home' with your actual home view name

    context = {
        'company': company,
        'projects': projects
    }
    return render(request, 'accounts/profile_view.html', context)

from employee.models import Employee
from department.models import Department
@login_required
def company_details(request):
    if request.user.role != 'company_owner':
        return redirect('user_login')

    company = request.user.company
    employees = Employee.objects.filter(company=company).select_related('designation', 'department')
    departments = Department.objects.filter(company=company)

    if request.method == 'POST':
        form = CompanySettingsForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            request.user.email = company.email
            request.user.first_name = company.name
            request.user.save()
            messages.success(request, "Company details updated successfully.")
            return redirect('company_details')
    else:
        form = CompanySettingsForm(instance=company)

    return render(request, 'accounts/company_details.html', {
        'company': company,
        'form': form,
        'total_employees': employees.count(),
        'total_departments': departments.count(),
        'employee_list': employees,
    })
from accounts.forms import JobSeekerSignUpForm

def jobseeker_signup_view(request):
    if request.method == 'POST':
        form = JobSeekerSignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'jobseeker'
            user.save()
            
            login(request, user)
            return redirect('jobseeker_dashboard') 
    else:
        form = JobSeekerSignUpForm()

    return render(request, 'accounts/jobseeker_signup.html', {'form': form})
