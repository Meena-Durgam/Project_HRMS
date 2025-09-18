from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Resignation
from .forms import ResignationForm
from employee.models import Employee
from django.contrib.auth.decorators import login_required

@login_required
def resignation_list(request):
    employee_obj = Employee.objects.get(user=request.user)
    resignations = Resignation.objects.all()

    if request.method == 'POST':
        form = ResignationForm(request.POST, request.FILES)
        if form.is_valid():
            resignation = form.save(commit=False)
            resignation.employee = employee_obj
            resignation.save()
            messages.success(request, 'Resignation submitted successfully.')
            return redirect('resignation_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ResignationForm()

    context = {
        'resignations': resignations,
        'form': form,
        'employee_obj': employee_obj,
    }
    return render(request, 'resignation_list.html', context)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resignation
from .forms import ResignationForm
from employee.models import Employee


@login_required
def add_resignation(request):
    try:
        employee_obj = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        messages.error(request, "Employee details not found.")
        return redirect('resignation_list')

    if request.method == 'POST':
        form = ResignationForm(request.POST, request.FILES)
        if form.is_valid():
            resignation = form.save(commit=False)
            resignation.employee = employee_obj
            resignation.save()
            messages.success(request, "Resignation submitted successfully.")
            return redirect('resignation_list')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = ResignationForm()

    return render(request, 'resignation_list.html', {
        'form': form,
        'employee_obj': employee_obj,
    })

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Resignation  # Assuming model name is Resignation
from .forms import ResignationForm  # Your resignation form
from django.contrib.auth.models import User


@login_required
def company_resignation_list(request):
    # Filter resignations by the company of the logged-in user (assuming company relation via employee)
    user_company = request.user.company if hasattr(request.user, 'company') else None
    
    # If company owner, show all resignations for the company
    if request.user.role == 'company_owner' and user_company:
        resignations = Resignation.objects.filter(employee__company=user_company).select_related('employee', 'employee__department')
    else:
        # For non-company_owner roles, restrict access or show empty list or redirect
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')  # Or another safe page

    # Prepare edit forms dict for resignations (if company owner needs to edit - optional)
    # Usually only employees can edit their own resignations, so this might be empty or not needed here
    edit_forms = {}

    context = {
        'resignations': resignations,
        'edit_forms': edit_forms,
    }
    return render(request, 'company_resignation_list.html', context)


@login_required
def update_resignation_status(request, resignation_id):
    # Only company_owner can update status
    if request.user.role != 'company_owner':
        messages.error(request, "You do not have permission to update resignation status.")
        return redirect('company_resignation_list')

    resignation = get_object_or_404(Resignation, id=resignation_id, employee__company=request.user.company)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'approved', 'rejected']:
            resignation.status = new_status
            resignation.save()
            messages.success(request, f"Resignation status updated to {new_status.capitalize()}.")
        else:
            messages.error(request, "Invalid status value.")
    return redirect('company_resignation_list')


# Optional: approve and reject views if you want separate URLs

from django.utils import timezone

@login_required
def approve_resignation(request, resignation_id):
    if request.user.role != 'company_owner':
        messages.error(request, "You do not have permission to approve resignations.")
        return redirect('company_resignation_list')

    resignation = get_object_or_404(Resignation, id=resignation_id, employee__company=request.user.company)
    resignation.status = 'approved'
    resignation.save()

    # Deactivate accounts only if last_working_day is today or earlier
    if resignation.last_working_day and resignation.last_working_day <= timezone.localdate():
        employee = resignation.employee
        employee.is_active = False
        employee.save()

        user = employee.user
        user.is_active = False
        user.save()

        messages.success(request, "Resignation approved. Employee account deactivated as of last working day.")
    else:
        messages.success(request, "Resignation approved. Employee account will be deactivated after last working day.")

    return redirect('company_resignation_list')



@login_required
def reject_resignation(request, resignation_id):
    if request.user.role != 'company_owner':
        messages.error(request, "You do not have permission to reject resignations.")
        return redirect('company_resignation_list')

    resignation = get_object_or_404(Resignation, id=resignation_id, employee__company=request.user.company)
    resignation.status = 'rejected'
    resignation.save()

    employee = resignation.employee
    employee.is_active = True
    employee.save()

    user = employee.user
    user.is_active = True
    user.save()

    messages.success(request, "Resignation rejected. Employee account activated.")
    return redirect('company_resignation_list')
