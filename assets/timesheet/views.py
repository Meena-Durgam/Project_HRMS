from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Timesheet
from .forms import TimesheetForm, TimesheetFilterForm
from django.utils.timezone import now, localtime
import csv
from functools import wraps
from django.contrib import messages
from decimal import Decimal
from django.db.models import Sum
from notifications.utils import notify_roles  # ✅ Add this

# Decorators
def employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "employee":
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied! Only Employees can perform this action.")
        return redirect("submit_timesheet")
    return _wrapped_view

def company_owner_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "company_owner":
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied! Only Company Owners can perform this action.")
        return redirect("all_timesheets")
    return _wrapped_view

# 1. EMPLOYEE: Submit Timesheet
@login_required
@employee_required
def submit_timesheet(request):
    employee = request.user.employee_account
    today = localtime(now()).date()
    timesheet = Timesheet.objects.filter(employee=employee, date=today).first()

    if request.method == 'POST':
        form = TimesheetForm(request.POST, request.FILES, employee=employee)
        if form.is_valid():
            if timesheet:
                timesheet.project = form.cleaned_data['project']
                timesheet.task_description = form.cleaned_data['task_description']
                timesheet.clock_in = form.cleaned_data['clock_in']
                timesheet.clock_out = form.cleaned_data['clock_out']
                timesheet.task_file = form.cleaned_data.get('task_file')
                if timesheet.clock_in and timesheet.clock_out:
                    timesheet.total_hours = timesheet.clock_out - timesheet.clock_in
                timesheet.save()
            else:
                new_timesheet = form.save(commit=False)
                new_timesheet.employee = employee
                new_timesheet.date = today
                if new_timesheet.clock_in and new_timesheet.clock_out:
                    new_timesheet.total_hours = new_timesheet.clock_out - new_timesheet.clock_in
                new_timesheet.save()

                # ✅ Notify company_owner
                notify_roles(
                    roles=['company_owner'],
                    message=f"{employee.user.username} submitted a new timesheet.",
                    url='/timesheets/all/',
                    sender=request.user
                )

            return redirect('submit_timesheet')
    else:
        form = TimesheetForm(instance=timesheet, employee=employee)

    project_name = request.GET.get('project', '')
    status = request.GET.get('status', '')
    timesheets = Timesheet.objects.filter(employee=employee)

    if project_name:
        timesheets = timesheets.filter(project__name__icontains=project_name)
    if status:
        timesheets = timesheets.filter(status=status)

    timesheets = timesheets.order_by('-date')
    total_logged = timesheets.aggregate(total_logged_seconds=Sum('total_hours'))['total_logged_seconds']

    if isinstance(total_logged, Decimal):
        total_logged = float(total_logged)

    return render(request, 'employee_timesheet.html', {
        'form': form,
        'timesheets': timesheets,
        'project_name': project_name,
        'status': status,
        'total_logged': total_logged,
    })

# 2. EMPLOYEE: Clock In
@login_required
@employee_required
def clock_in(request):
    employee = request.user.employee_account
    today = localtime(now()).date()

    try:
        timesheet, created = Timesheet.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={'clock_in': localtime(now())}
        )

        if created or not timesheet.clock_in:
            timesheet.clock_in = localtime(now())
            timesheet.save()
            messages.success(request, 'Clock-in successful!')

            # Notify company_owner
            notify_roles(
                roles=['company_owner'],
                message=f"{employee.user.username} clocked in today.",
                url='/timesheets/all/',
                sender=request.user
            )
        else:
            messages.info(request, 'You have already clocked in today.')

    except Exception as e:
        messages.error(request, f"Error: {str(e)}")

    return redirect('submit_timesheet')


# 2. EMPLOYEE: Clock Out
@login_required
@employee_required
def clock_out(request):
    employee = request.user.employee_account
    today = localtime(now()).date()

    try:
        timesheet = Timesheet.objects.get(employee=employee, date=today)

        if not timesheet.clock_in:
            messages.error(request, "Cannot clock out before clocking in.")
        elif timesheet.clock_out:
            messages.info(request, "You have already clocked out today.")
        else:
            timesheet.clock_out = localtime(now())
            timesheet.total_hours = timesheet.clock_out - timesheet.clock_in
            timesheet.save()
            messages.success(request, "Successfully clocked out!")

    except Timesheet.DoesNotExist:
        messages.error(request, "No clock-in record found for today.")

    return redirect('submit_timesheet')


# 3. COMPANY OWNER: View & Filter Timesheets
@login_required
@company_owner_required
def all_timesheets(request):
    form = TimesheetFilterForm(request.GET or None)
    timesheets = Timesheet.objects.filter(employee__company=request.user.company).order_by('-date')

    if form.is_valid():
        if form.cleaned_data.get('project'):
            timesheets = timesheets.filter(project=form.cleaned_data['project'])
        if form.cleaned_data.get('employee'):
            timesheets = timesheets.filter(employee=form.cleaned_data['employee'])
        if form.cleaned_data.get('date'):
            timesheets = timesheets.filter(date=form.cleaned_data['date'])
        if form.cleaned_data.get('status'):
            timesheets = timesheets.filter(status=form.cleaned_data['status'])

    return render(request, 'admin_timesheet.html', {
        'timesheets': timesheets,
        'form': form
    })

# 4. COMPANY OWNER: Update Status (Approve/Reject)
@login_required
@company_owner_required
def update_timesheet_status(request, pk, status):
    timesheet = get_object_or_404(Timesheet, pk=pk, employee__company=request.user.company)

    if status not in ['Pending', 'Approved', 'Rejected']:
        return HttpResponse("Invalid status", status=400)

    timesheet.status = status
    timesheet.save()

    # ✅ Notify the employee
    notify_roles(
        roles=['employee'],
        message=f"Your timesheet on {timesheet.date} has been marked as {status}.",
        url='/timesheets/',
        sender=request.user
    )

    messages.success(request, f"Timesheet marked as {status}.")
    return redirect('all_timesheets')
