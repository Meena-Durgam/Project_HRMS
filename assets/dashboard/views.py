from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from collections import OrderedDict
from decimal import Decimal, ROUND_HALF_UP  
from calendar import month_abbr
import json
from django.db.models import Count, Q, Avg
from projects.models import Project, Task,TaskProgress
from clients.models import Client
from employee.models import Employee, EmployeeProfile
from invoices.models import Invoice
from leave_management.models import LeaveType,LeaveRequest,LeaveBalance
from goal.models import Goal
from performance.models import PerformanceAppraisal
from holiday.models import Holiday
from django.contrib import messages


@login_required
def company_owner_dashboard(request):
    if request.user.role != 'company_owner':
        return HttpResponseForbidden("Unauthorized Access")

    company = request.user.company

    # 🚨 Check if profile is incomplete
    if not company.complete_profile:
        messages.warning(request, "Please complete your company profile to Access All Features.")

    # Basic counts
    total_projects = Project.objects.filter(company=company).count()
    total_clients = Client.objects.filter(company=company).count()
    tasks = Task.objects.filter(project__company=company)
    total_employees = Employee.objects.filter(company=company).count()

    # New employees (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_employees = Employee.objects.filter(company=company, created_at__gte=thirty_days_ago).count()
    employee_percent = (new_employees / total_employees) * 100 if total_employees else 0
    employees = Employee.objects.filter(company=company)

    # Monthly Income & Outcome
    current_year = timezone.now().year

    monthly_invoices = (
        Invoice.objects
        .filter(company=company, invoice_date__year=current_year)
        .annotate(month=TruncMonth('invoice_date'))
        .values('month')
        .annotate(total=Sum('grand_total'))
        .order_by('month')
    )

    monthly_data = OrderedDict((i, {'income': 0, 'outcome': 0}) for i in range(1, 13))
    for entry in monthly_invoices:
        month_num = entry['month'].month
        monthly_data[month_num]['income'] = float(entry['total'])

    for month in monthly_data:
        monthly_data[month]['outcome'] = round(monthly_data[month]['income'] * 0.6, 2)

    # Format for frontend charts
    sales_data = {
        'labels': [month_abbr[m] for m in monthly_data.keys()],
        'income': [monthly_data[m]['income'] for m in monthly_data],
        'outcome': [monthly_data[m]['outcome'] for m in monthly_data],
    }

    # Earnings and expenses (current month vs previous)
    now = timezone.now()
    current_month = now.month
    previous_month = (now - timedelta(days=30)).month

    earnings = monthly_data[current_month]['income'] if current_month in monthly_data else 0
    previous_earnings = monthly_data[previous_month]['income'] if previous_month in monthly_data else 0

    earnings_change = ((Decimal(earnings) - Decimal(previous_earnings)) / Decimal(previous_earnings) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if previous_earnings else Decimal('0.00')
    earnings_bar = float(earnings_change) if earnings_change > 0 else 0

    expenses = Decimal(earnings) * Decimal('0.6')
    previous_expenses = Decimal(previous_earnings) * Decimal('0.6')
    expense_change = ((expenses - previous_expenses) / previous_expenses * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if previous_expenses else Decimal('0.00')
    expenses_bar = float(expense_change) if expense_change > 0 else 0

    profit = Decimal(earnings) - expenses
    previous_profit = Decimal(previous_earnings) - previous_expenses
    profit_change = ((profit - previous_profit) / previous_profit * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if previous_profit else Decimal('0.00')
    profit_bar = float(profit_change) if profit_change > 0 else 0

    # Latest invoices and clients
    invoices = Invoice.objects.filter(company=company).order_by('-invoice_date')[:5]
    clients = Client.objects.filter(company=company).order_by('-id')[:5]

    # Employee list
    employees = Employee.objects.filter(company=company).select_related('user')

    context = {
        'company': company,
        'owner': request.user,
        'total_projects': total_projects,
        'total_clients': total_clients,
        'tasks': tasks,
        'total_employees': total_employees,
        'new_employees': new_employees,
        'employee_percent': round(employee_percent, 2),
        'earnings': float(earnings),
        'previous_earnings': float(previous_earnings),
        'earnings_change': float(earnings_change),
        'earnings_bar': earnings_bar,
        'expenses': float(expenses),
        'previous_expenses': float(previous_expenses),
        'expense_change': float(expense_change),
        'expenses_bar': expenses_bar,
        'profit': float(profit),
        'previous_profit': float(previous_profit),
        'profit_change': float(profit_change),
        'profit_bar': profit_bar,
        'invoices': invoices,
        'clients': clients,
        'employees': [e.user for e in employees if e.user],
        'sales_data': json.dumps(sales_data),
    }

    return render(request, 'company_owner_dashboard.html', context)


from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.shortcuts import render

@login_required
def employee_dashboard(request):
    user = request.user
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)

    try:
        employee = user.employee_account
    except:
        return render(request, 'error.html', {'message': 'Employee Account Not Found.'})

    # ✅ Profile completion check
    profile = getattr(employee, 'profile', None)
    is_profile_complete = profile.is_completed if profile else False
    is_profile_editable = not is_profile_complete

    # ✅ Leave info
    leaves_today = LeaveRequest.objects.filter(
        start_date__lte=today,
        end_date__gte=today,
        status='Approved'
    )

    leaves_tomorrow = LeaveRequest.objects.filter(
        start_date__lte=tomorrow,
        end_date__gte=tomorrow,
        status='Approved'
    )

    leaves_next_week = LeaveRequest.objects.filter(
        start_date__range=(today, next_week),
        status='Approved'
    )

    # ✅ Project and Task info (include leader + member)
    projects = Project.objects.filter(
        Q(team_leader=employee) | Q(team_members=employee)
    ).distinct()
    total_projects = projects.count()

    leader_projects_count = Project.objects.filter(team_leader=employee).count()
    member_projects_count = Project.objects.filter(team_members=employee).exclude(team_leader=employee).count()

    tasks = Task.objects.filter(project__in=projects)
    total_tasks = tasks.count()
    pending_tasks = tasks.filter(status='Pending').count()

    # ✅ Leave Balance & Summary
    leave_balances = LeaveBalance.objects.filter(employee=employee)

    leave_summary = []
    total_used = 0
    total_remaining = 0
    for balance in leave_balances:
        leave_type = balance.leave_type
        used = balance.used_days
        remaining = balance.remaining_days()
        total = leave_type.default_days

        leave_summary.append({
            'leave_type': leave_type.name,
            'total': total,
            'used': used,
            'remaining': remaining
        })

        total_used += used
        total_remaining += remaining

    # ✅ Upcoming Holiday
    upcoming = Holiday.objects.filter(
        date__gte=today,
        company=employee.company
    ).order_by('date').first()

    upcoming_holiday = (
        f"{upcoming.date.strftime('%a %d %B %Y')} – {upcoming.name}"
        if upcoming else "No Upcoming Holidays."
    )

    context = {
        "today_date": today,
        "today_status": [f"{l.employee} Is Off Today" for l in leaves_today],
        "tomorrow_status": f"{leaves_tomorrow.count()} People Will be Away Tomorrow",
        "next_7_days": [f"{l.employee} Will be Away From {l.start_date.strftime('%A')}" for l in leaves_next_week],

        # Projects & Tasks
        "total_projects": total_projects,
        "leader_projects_count": leader_projects_count,
        "member_projects_count": member_projects_count,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,

        # Leave
        "leave_summary": leave_summary,
        "leave_taken": total_used,
        "leave_remaining": total_remaining,

        # Other
        "upcoming_holiday": upcoming_holiday,
        "is_profile_complete": is_profile_complete,
        "is_profile_editable": is_profile_editable,
    }

    return render(request, 'employee_dashboard.html', context)


def home(request):
    return render(request, 'home.html')

@login_required
def jobseeker_dashboard(request):
    # Ensure only jobseekers access this view
    return render(request, 'jobseeker_dashboard.html')
