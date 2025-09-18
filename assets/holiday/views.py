from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from datetime import datetime, date
import csv
from .models import Holiday
from django.conf import settings
from .forms import HolidayForm
import logging
from calendar import month_name
from django.contrib import messages

from notifications.utils import notify_roles  # ✅ Import notifications

logger = logging.getLogger(__name__)

API_KEY = settings.CALENDARIFIC_API_KEY
COUNTRY_CODE = 'IN'


def holiday_list(request):
    user = request.user
    user_role = user.role
    current_year = datetime.now().year

    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')

    try:
        filter_year = int(selected_year)
    except (TypeError, ValueError):
        filter_year = current_year

    try:
        filter_month = int(selected_month)
    except (TypeError, ValueError):
        filter_month = None

    # For dropdown options
    years = range(current_year - 5, current_year + 6)
    months = [date(2000, m, 1) for m in range(1, 13)]
    month_names = [month_name[m] for m in range(1, 13)]

    # ✅ Skip API holidays (leave this empty if not displaying them)
    holidays = []

    # ✅ Filter manually added holidays
    manually_added_holidays = (
        Holiday.objects.all()
        if user.role == 'superadmin'
        else Holiday.objects.filter(company=user.company)
    )

    # ✅ Apply year and month filters
    manually_added_holidays = manually_added_holidays.filter(date__year=filter_year)
    if filter_month:
        manually_added_holidays = manually_added_holidays.filter(date__month=filter_month)

    manually_added_holidays = manually_added_holidays.order_by('date')

    no_holidays_found = not manually_added_holidays.exists()

    # ✅ Handle manual holiday addition
    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            holiday = form.save(commit=False)
            holiday.company = user.company
            holiday.save()

            # ✅ Success message
            messages.success(request, f"Holiday added successfully.")

            # ✅ Notify employees
            notify_roles(
                roles=['employee'],
                message=f"{user.username} added a new holiday: '{holiday.name}' on {holiday.date}.",
                url='/holidays/',
                sender=user
            )

            return redirect('holiday_list')
    else:
        form = HolidayForm()

    return render(request, 'holiday.html', {
        'holidays': holidays,  # empty list
        'manually_added_holidays': manually_added_holidays,
        'selected_year': filter_year,
        'selected_month': filter_month,
        'years': years,
        'months': months,
        'month_names': month_names,
        'form': form,
        'user_role': user_role,
        'no_holidays_found': no_holidays_found,
    })


def add_holiday(request):
    """Not needed separately since holiday_list handles add,
    but keeping for reference if you use a separate add page."""
    user = request.user
    user_role = user.role
    current_year = datetime.now().year
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')

    try:
        filter_year = int(selected_year)
    except (TypeError, ValueError):
        filter_year = current_year

    try:
        filter_month = int(selected_month)
    except (TypeError, ValueError):
        filter_month = None

    # 📅 Filter manually added holidays
    manually_added_holidays = (
        Holiday.objects.all()
        if user_role == 'superadmin'
        else Holiday.objects.filter(company=user.company)
    )

    manually_added_holidays = manually_added_holidays.filter(date__year=filter_year)
    if filter_month:
        manually_added_holidays = manually_added_holidays.filter(date__month=filter_month)

    manually_added_holidays = manually_added_holidays.order_by('date')

    years = range(current_year - 5, current_year + 6)
    months = [date(2000, m, 1) for m in range(1, 13)]

    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            holiday = form.save(commit=False)
            holiday.company = user.company
            holiday.save()

            messages.success(request, f"Holiday added successfully.")

            notify_roles(
                roles=['employee'],
                message=f"{user.username} added a new holiday: '{holiday.name}' on {holiday.date}.",
                url='/holidays/',
                sender=user
            )
            return redirect('holiday_list')
    else:
        form = HolidayForm()

    return render(request, 'holiday.html', {
        'form': form,
        'manually_added_holidays': manually_added_holidays,
        'selected_year': filter_year,
        'selected_month': filter_month,
        'years': years,
        'months': months,
        'user_role': user_role,
        'add_mode': True
    })


def edit_holiday(request, id):
    holiday = get_object_or_404(Holiday, id=id, company=request.user.company)

    if request.method == 'POST':
        form = HolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()

            # ✅ Success message
            messages.success(request, f"Holiday updated successfully.")

            # ✅ Notify employees
            notify_roles(
                roles=['employee'],
                message=f"{request.user.username} updated the holiday: '{holiday.name}' to {holiday.date}.",
                url='/holidays/',
                sender=request.user
            )

            return redirect('holiday_list')
    else:
        form = HolidayForm(instance=holiday)

    return render(request, 'holiday.html', {'form': form, 'holiday': holiday})


def delete_holiday(request, id):
    holiday = get_object_or_404(Holiday, id=id, company=request.user.company)
    name = holiday.name
    date_str = holiday.date
    holiday.delete()

    # ✅ Success message
    messages.success(request, f"Holiday deleted successfully.")

    # ✅ Notify employees
    notify_roles(
        roles=['employee'],
        message=f"{request.user.username} deleted the holiday: '{name}' originally on {date_str}.",
        url='/holidays/',
        sender=request.user
    )

    return redirect('holiday_list')


def export_holidays_csv(request):
    if request.user.role == 'superadmin':
        holidays = Holiday.objects.all().order_by('date')
    else:
        holidays = Holiday.objects.filter(company=request.user.company).order_by('date')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="holidays.csv"'
    writer = csv.writer(response)
    writer.writerow(['Holiday Name', 'Date'])

    for h in holidays:
        writer.writerow([h.name, h.date])

    return response
