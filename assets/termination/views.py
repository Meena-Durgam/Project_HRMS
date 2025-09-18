from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Termination
from .forms import TerminationForm
from employee.models import Employee
from department.models import Department
from notifications.utils import notify_roles
from django.db.models import Q
from django.core.paginator import Paginator

  # ✅ Notification system


# ✅ Check if user is a company owner
def is_company_owner(user):
    return hasattr(user, 'role') and user.role == 'company_owner'

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect

from .models import Termination
from employee.models import Employee, Department
from .forms import TerminationForm


@login_required
def termination_list(request):
    company = request.user.company
    user_role = getattr(request.user, 'role', '')

    # Get all terminations for the company
    terminations = Termination.objects.filter(company=company).select_related('employee', 'employee__department').order_by('-id')

    # Filter terminations based on GET query params (employee name or department name)
    employee_query = request.GET.get('employee')
    department_query = request.GET.get('department')

    if employee_query:
        terminations = terminations.filter(
            Q(employee__first_name__icontains=employee_query) |
            Q(employee__last_name__icontains=employee_query)
        )

    if department_query:
        terminations = terminations.filter(employee__department__name__icontains=department_query)

    # Only active employees shown for selection
    employees = Employee.objects.filter(company=company, status='Active').select_related('department')

    # Departments for filtering in the UI
    departments = Department.objects.filter(company=company)

    # Initialize form with filtered employees queryset and user context
    form = TerminationForm(request.POST or None, user=request.user)

    if request.method == 'POST' and 'add_termination' in request.POST:
        if form.is_valid():
            termination = form.save(commit=False)
            termination.company = company
            termination.save()

            employee = termination.employee
            today = timezone.now().date()

            # Deactivate employee and linked user if termination date has passed or is today
            if termination.termination_date <= today:
                if employee.status != 'Inactive':
                    employee.status = 'Inactive'
                    employee.save(update_fields=['status'])

                    if employee.user:
                        employee.user.is_active = False
                        employee.user.save(update_fields=['is_active'])

                # Delete the employee record from database
                employee.delete()

            messages.success(request, 'Termination added and employee deactivated successfully.')

            # Notify employees about termination event
            notify_roles(
                roles=['employee'],
                message=f"Employee '{employee.first_name} {employee.last_name}' has been terminated by {request.user.username}.",
                url='/termination/',
                sender=request.user
            )

            return redirect('termination_list')
        else:
            messages.error(request, 'There was an error in the form.')

    if user_role != 'company_owner':
        # Restrict view for non-owners, no form, no employees listed
        return render(request, 'termination_list.html', {
            'terminations': terminations,
            'form': None,
            'employees': [],
            'user_role': user_role,
        })

    # Render page with active employees, full terminations list and form
    return render(request, 'termination_list.html', {
        'terminations': terminations,
        'employees': employees,
        'departments': departments,
        'form': form,
        'user_role': user_role,
    })

# ✅ View: Edit Termination
@login_required
@user_passes_test(is_company_owner)
def edit_termination(request, pk):
    company = request.user.company
    termination = get_object_or_404(Termination, pk=pk, company=company)

    if request.method == 'POST':
        form = TerminationForm(request.POST, instance=termination, user=request.user)
        if form.is_valid():
            termination = form.save()
            employee = termination.employee
            today = timezone.now().date()

            # ✅ Deactivate employee and user if termination date is today or earlier
            if termination.termination_date <= today:
                if employee.status != 'Inactive':
                    employee.status = 'Inactive'
                    employee.save(update_fields=['status'])
                    if employee.user:
                        employee.user.is_active = False
                        employee.user.save(update_fields=['is_active'])

            messages.success(request, 'Termination updated successfully.')

            # ✅ Notify employees
            notify_roles(
                roles=['employee'],
                message=f"Termination details for '{employee.first_name} {employee.last_name}' were updated by {request.user.username}.",
                url='/termination/',
                sender=request.user
            )

        else:
            messages.error(request, 'Invalid form data.')

        return redirect('termination_list')

    messages.error(request, 'Invalid request method.')
    return redirect('termination_list')


# ✅ View: Delete Termination and Reactivate Employee
@login_required
@user_passes_test(is_company_owner)
def delete_termination(request, pk):
    company = request.user.company
    termination = get_object_or_404(Termination, pk=pk, company=company)

    if request.method == 'POST':
        employee = termination.employee
        termination.delete()

        # ✅ Reactivate employee and user
        if employee.status == 'Inactive':
            employee.status = 'Active'
            employee.save(update_fields=['status'])

            if employee.user:
                employee.user.is_active = True
                employee.user.save(update_fields=['is_active'])

        messages.success(request, 'Termination deleted and employee reactivated.')

        # ✅ Notify employees
        notify_roles(
            roles=['employee'],
            message=f"Termination of '{employee.first_name} {employee.last_name}' was removed by {request.user.username}.",
            url='/termination/',
            sender=request.user
        )

    return redirect('termination_list')
