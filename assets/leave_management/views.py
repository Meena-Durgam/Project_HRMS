from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import LeaveType, LeaveRequest, LeaveBalance
from .forms import LeaveTypeForm, LeaveRequestForm
from accounts.models import CustomUser, Company
from employee.models import Employee

from notifications.utils import notify_roles


# --- Role Check Utilities ---
def is_company_owner(user):
    return user.role == 'company_owner' and user.company is not None

def is_employee(user):
    return user.role == 'employee' and hasattr(user, 'employee_account') and user.company is not None


# ✅ EMPLOYEE: Apply & View Leave
from collections import defaultdict

@login_required
def employee_leave(request):
    if not is_employee(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    employee = request.user.employee_account
    company = request.user.company

    edit_leave_id = request.GET.get('edit')
    edit_instance = None

    if edit_leave_id:
        try:
            edit_instance = LeaveRequest.objects.get(
                id=edit_leave_id,
                employee=employee,
                status='Pending'
            )
        except LeaveRequest.DoesNotExist:
            messages.warning(request, "Leave not found or not editable.")
            return redirect('employee_leave')

    form = LeaveRequestForm(instance=edit_instance)
    form.fields['leave_type'].queryset = LeaveType.objects.filter(company=company)

    if request.method == 'POST':
        if 'apply_leave' in request.POST:
            form = LeaveRequestForm(request.POST)
        elif 'update_leave' in request.POST and edit_instance:
            form = LeaveRequestForm(request.POST, instance=edit_instance)

        form.fields['leave_type'].queryset = LeaveType.objects.filter(company=company)

        if form.is_valid():
            leave_type = form.cleaned_data['leave_type']

            # ✅ Check leave balance
            leave_balance = LeaveBalance.objects.filter(employee=employee, leave_type=leave_type).first()
            if not leave_balance or leave_balance.remaining_days() <= 0:
                messages.error(request, f"You have no remaining days for {leave_type.name}. Leave request not submitted.")
                return redirect('employee_leave')

            leave = form.save(commit=False)
            leave.employee = employee
            leave.company = company
            leave.save()

            notify_roles(
                roles=['company_owner'],
                message=f"{request.user.username} submitted a leave request ({leave.leave_type.name}, {leave.start_date} to {leave.end_date}).",
                url="/leave/review/",
                sender=request.user
            )

            if edit_instance:
                messages.success(request, "Leave request updated successfully.")
            else:
                messages.success(request, "Leave request submitted successfully.")
            return redirect('employee_leave')

    leave_balances = LeaveBalance.objects.filter(employee=employee)
    leaves = LeaveRequest.objects.filter(employee=employee).order_by('-applied_at')

    leave_history = []
    summary_counts = defaultdict(int)
    total_approved_days = 0
    pending_request_count = 0

    for leave in leaves:
        days = (leave.end_date - leave.start_date).days + 1
        leave_history.append({'leave': leave, 'days_count': days})

        if leave.status == 'Approved':
            total_approved_days += days
            summary_counts[leave.leave_type.name] += days

        if leave.status == 'Pending':
            pending_request_count += 1

    medical_balance = leave_balances.filter(leave_type__name__iexact="Medical Leave").first()
    remaining_medical = medical_balance.remaining_days() if medical_balance else 0

    return render(request, 'employee_leave.html', {
        'form': form,
        'edit_instance': edit_instance,
        'leaves': leave_history,
        'leave_balances': leave_balances,
        'remaining_days_json': {str(lb.leave_type.id): lb.remaining_days() for lb in leave_balances},
        'summary': {
            'total': total_approved_days,
            'medical': remaining_medical,
            'pending': pending_request_count,
            'remaining': sum(lb.remaining_days() for lb in leave_balances),
            'remaining_total': sum(lb.remaining_days() for lb in leave_balances),
        }
    })


@login_required
def delete_leave(request, leave_id):
    if not is_employee(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    employee = request.user.employee_account
    leave = get_object_or_404(LeaveRequest, id=leave_id, employee=employee)

    if leave.status != 'Pending':
        messages.warning(request, "Only pending leave requests can be deleted.")
        return redirect('employee_leave')

    leave.delete()

    # Line: ~118
    notify_roles(
        roles=['company_owner'],
        message=f"{request.user.username} deleted their leave request ({leave.leave_type.name}, {leave.start_date} to {leave.end_date}).",
        url="/leave/review/",
        sender=request.user
    )

    messages.success(request, "Leave request deleted successfully.")
    return redirect('employee_leave')



# ✅ COMPANY OWNER: Manage Leave Types & Requests
@login_required
def company_owner_leave(request):
    if not is_company_owner(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    company = request.user.company
    leave_type_form = LeaveTypeForm()

    if request.method == 'POST' and 'add_leave_type' in request.POST:
        leave_type_form = LeaveTypeForm(request.POST)
        if leave_type_form.is_valid():
            leave_type = leave_type_form.save(commit=False)
            leave_type.company = company
            leave_type.save()
            
            notify_roles(
                roles=['employee'],
                message=f"New leave type '{leave_type.name}' added by {request.user.username}.",
                url="/employee/leave/",
                sender=request.user
            )

            # Assign to all employees in the company
            employees = Employee.objects.filter(company=company)
            for emp in employees:
                LeaveBalance.objects.get_or_create(
                    employee=emp,
                    leave_type=leave_type,
                    defaults={'used_days': 0}
                )

            messages.success(request, "Leave type added and assigned to all employees.")
            return redirect('company_owner_leave')

    leave_types = LeaveType.objects.filter(company=company)
    leave_requests = LeaveRequest.objects.filter(company=company).order_by('-applied_at')

    return render(request, 'company_owner_leave.html', {
        'leave_type_form': leave_type_form,
        'leave_types': leave_types,
        'leave_requests': leave_requests,
    })

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db.models import Q

from django.db.models import Q
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

@login_required
def create_leave_type_and_assign(request):
    if not is_company_owner(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    company = request.user.company
    form = LeaveTypeForm()

    # ✅ Get filter inputs from GET params
    search_query = request.GET.get('search', '').strip()
    eligibility_filter = request.GET.get('eligibility', '').strip()

    # ✅ Base queryset
    leave_types_qs = LeaveType.objects.filter(company=company)

    # ✅ Apply filters if provided
    if search_query:
        leave_types_qs = leave_types_qs.filter(Q(name__icontains=search_query))
    if eligibility_filter:
        leave_types_qs = leave_types_qs.filter(eligibility=eligibility_filter)

    leave_types_qs = leave_types_qs.order_by('name')

    # ✅ Pagination with dynamic page size
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 5)  # Default to 5 per page

    try:
        page_size = int(page_size)
        if page_size <= 0:
            page_size = 5
    except ValueError:
        page_size = 5

    paginator = Paginator(leave_types_qs, page_size)

    try:
        leave_types = paginator.page(page)
    except PageNotAnInteger:
        leave_types = paginator.page(1)
    except EmptyPage:
        leave_types = paginator.page(paginator.num_pages)

    # ✅ Edit forms for visible items
    edit_forms = {lt.id: LeaveTypeForm(instance=lt, prefix=str(lt.id)) for lt in leave_types}

    # ✅ Handle creation form
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            leave_type = form.save(commit=False)
            leave_type.company = company

            if LeaveType.objects.filter(name=leave_type.name, company=company).exists():
                messages.error(request, f"Leave type already exists.")
            else:
                leave_type.save()
                messages.success(request, f"Leave type created successfully.")
                return redirect('create_leave_type')

    return render(request, 'create_leave_type.html', {
        'form': form,
        'leave_types': leave_types,
        'edit_forms': edit_forms,
        'search_query': search_query,
        'eligibility_filter': eligibility_filter,
        'page_size': page_size,  # ✅ pass to template
    })


@login_required
def assign_leave_balance(request, leave_type_id):
    if not is_company_owner(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    company = request.user.company
    employees = Employee.objects.filter(company=company).select_related('profile')

    try:
        leave_type = LeaveType.objects.get(id=leave_type_id, company=company)
    except LeaveType.DoesNotExist:
        messages.error(request, "Leave type not found.")
        return redirect('create_leave_type')

    # Filter employees based on leave type eligibility
    if leave_type.eligibility == 'male':
        eligible_employees = employees.filter(profile__gender__iexact='Male')
    elif leave_type.eligibility == 'female':
        eligible_employees = employees.filter(profile__gender__iexact='Female')
    else:  # 'all' or empty
        eligible_employees = employees

    assigned_count = 0
    for emp in eligible_employees:
        balance, created = LeaveBalance.objects.get_or_create(
            employee=emp,
            leave_type=leave_type,
            company=company,
            defaults={'used_days': 0}
        )
        if created:
            assigned_count += 1

    messages.success(request, f"Assigned {assigned_count} leave balances for {leave_type.name}.")
    return redirect('create_leave_type')



from django.db import transaction

@login_required
def edit_leave_type(request, type_id):
    leave_type = get_object_or_404(LeaveType, id=type_id, company=request.user.company)

    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type, prefix=str(leave_type.id))
        if form.is_valid():
            with transaction.atomic():
                updated_leave_type = form.save()

                notify_roles(
                    roles=['employee'],
                    message=f"Leave type '{updated_leave_type.name}' was updated by {request.user.username}.",
                    url="/employee/leave/",
                    sender=request.user
                )

            messages.success(request, "Leave type updated successfully.")

    return redirect('create_leave_type')

@login_required
def delete_leave_type(request, type_id):
    leave_type = get_object_or_404(LeaveType, id=type_id, company=request.user.company)
    leave_type.delete()

    
    notify_roles(
        roles=['employee'],
        message=f"Leave type '{leave_type.name}' was removed by {request.user.username}.",
        url="/employee/leave/",
        sender=request.user
    )

    messages.success(request, "Leave type deleted successfully.")
    return redirect('create_leave_type')

from django.views.decorators.http import require_POST

from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db import transaction

@login_required
def review_all_leave_requests(request):
    if not is_company_owner(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    company = request.user.company
    leave_requests = LeaveRequest.objects.filter(company=company).select_related('employee', 'leave_type').order_by('-applied_at')
    leave_types = LeaveType.objects.filter(company=company).order_by('name')

    # 🔍 Filtering
    employee_name = request.GET.get('employee_name', '').strip()
    leave_type_id = request.GET.get('leave_type', '').strip()
    status = request.GET.get('status', '').strip()
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if employee_name:
        leave_requests = leave_requests.filter(
            employee__first_name__icontains=employee_name
        )

    if leave_type_id.isdigit():
        leave_requests = leave_requests.filter(leave_type__id=int(leave_type_id))

    if status:
        leave_requests = leave_requests.filter(status=status)

    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            leave_requests = leave_requests.filter(start_date__gte=from_date_obj)
        except ValueError:
            pass

    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            leave_requests = leave_requests.filter(end_date__lte=to_date_obj)
        except ValueError:
            pass

    # 🧮 Calculate no. of days
    for leave in leave_requests:
        if leave.start_date and leave.end_date:
            leave.no_of_days = (leave.end_date - leave.start_date).days + 1
        else:
            leave.no_of_days = 0

    # ✅ Handle Approval/Reject
    if request.method == 'POST':
        leave_id = request.POST.get('leave_id')
        action = request.POST.get('action')

        leave = get_object_or_404(LeaveRequest, id=leave_id, company=company)

        if leave.status != 'Pending':
            messages.warning(request, f"Leave request by {leave.employee} already processed.")
        else:
            if action == 'approve':
                with transaction.atomic():
                    leave.status = 'Approved'
                    leave.reviewed_by = request.user
                    leave.save()

                    # 🔑 Deduct from LeaveBalance
                    try:
                        balance = LeaveBalance.objects.get(
                            employee=leave.employee,
                            leave_type=leave.leave_type,
                            company=company
                        )

                        no_of_days = (leave.end_date - leave.start_date).days + 1

                        balance.used_days += no_of_days
                        balance.save()

                    except LeaveBalance.DoesNotExist:
                        messages.error(request, f"No leave balance found for {leave.employee} - {leave.leave_type}.")
                        return redirect('review_all_leave_requests')

                messages.success(request, f"{leave.employee}'s leave approved.")
            
            elif action == 'reject':
                leave.status = 'Rejected'
                leave.reviewed_by = request.user
                leave.save()
                messages.success(request, f"{leave.employee}'s leave rejected successfully.")

        return redirect('review_all_leave_requests')

    return render(request, 'company_owner_leave.html', {
        'leave_requests': leave_requests,
        'leave_types': leave_types,
        'filters': {
            'employee_name': employee_name,
            'leave_type': leave_type_id,
            'status': status,
            'from_date': from_date,
            'to_date': to_date,
        }
    })



# ✅ COMPANY OWNER: Approve/Reject Individual Leave Request
@login_required
@require_http_methods(["GET"])
def review_leave_request(request, leave_id, action):
    if not is_company_owner(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    company = request.user.company
    leave = get_object_or_404(LeaveRequest, pk=leave_id, company=company)

    if leave.status != 'Pending':
        messages.warning(request, "Leave has already been reviewed.")
        return redirect('company_owner_leave')

    if action == 'approve':
        duration = (leave.end_date - leave.start_date).days + 1

        balance, _ = LeaveBalance.objects.get_or_create(
            employee=leave.employee,
            leave_type=leave.leave_type,
            defaults={'used_days': 0}
        )

        remaining = leave.leave_type.default_days - balance.used_days
        if remaining < duration:
            messages.error(request, f"Insufficient balance. Only {remaining} days remaining.")
            return redirect('company_owner_leave')

        balance.used_days += duration
        balance.save()

        leave.status = 'Approved'
        messages.success(request, f"Leave request approved. {duration} day(s) deducted.")
        
    elif action == 'reject':
        leave.status = 'Rejected'
        messages.info(request, "Leave request rejected.")


        

    else:
        messages.error(request, "Invalid action.")
        return redirect('company_owner_leave')

    leave.reviewed_by = request.user
    leave.reviewed_at = timezone.now()
    leave.save()
    

    return redirect('company_owner_leave')