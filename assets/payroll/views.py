from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PayItemForm
from .models import PayItem
from django.http import JsonResponse
@login_required
def manage_payitems(request, pk=None):
    company = request.user.company
    payitems = PayItem.objects.filter(company=company)

    if pk:
        payitem = get_object_or_404(PayItem, pk=pk, company=company)
        form = PayItemForm(request.POST or None, instance=payitem, company=company)
        edit_mode = True
    else:
        payitem = None
        form = PayItemForm(request.POST or None, company=company)
        edit_mode = False

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.company = company
            instance.save()
            form.save_m2m()
            return redirect('manage_payitems')
    categories = [
        ('earning', 'Additions'),
        ('deduction', 'Deductions'),
    ]
    return render(request, 'manage_payitems.html', {
        'form': form,
        'categories': categories,
        'payitems': payitems,
        'edit_mode': edit_mode,
        'editing_item': payitem
    })

@login_required
def delete_payitem(request, pk):
    payitem = get_object_or_404(PayItem, pk=pk, company=request.user.company)
    payitem.delete()
    return redirect('manage_payitems')

@login_required
def edit_payitem(request):
    if request.method == 'POST':
        pk = request.POST.get('item_id')
        payitem = get_object_or_404(PayItem, pk=pk, company=request.user.company)
        form = PayItemForm(request.POST, instance=payitem, company=request.user.company)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.company = request.user.company
            instance.save()
            form.save_m2m()
            return redirect('manage_payitems')
    return redirect('manage_payitems')

from django.http import JsonResponse
from django.db.models import Q
from employee.models import Employee
from .models import PayItem

def get_employee_payitems(request, employee_id):
    try:
        employee = Employee.objects.get(id=employee_id)

        # Earnings: Assigned to all or specifically to this employee
        earnings = PayItem.objects.filter(
            item_type='earning'
        ).filter(
            Q(assign_to='all') | Q(specific_employees=employee)
        ).distinct()

        # Deductions: Assigned to all or specifically to this employee
        deductions = PayItem.objects.filter(
            item_type='deduction'
        ).filter(
            Q(assign_to='all') | Q(specific_employees=employee)
        ).distinct()

        data = {
            'earnings': [{'title': item.title, 'amount': float(item.amount)} for item in earnings],
            'deductions': [{'title': item.title, 'amount': float(item.amount)} for item in deductions]
        }
        return JsonResponse(data)

    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Payroll
from .forms import PayrollForm

def manage_payroll(request):
    payrolls = Payroll.objects.select_related('employee', 'company').all()
    pay_items = []  # Default empty

    if request.method == 'POST':
        if 'edit_id' in request.POST:
            # Editing an existing payroll
            instance = get_object_or_404(Payroll, id=request.POST.get('edit_id'))
            form = PayrollForm(request.POST, instance=instance, company=instance.company)
            pay_items = PayItem.objects.filter(specific_employees=instance.employee)
            if form.is_valid():
                payroll = form.save(commit=False)
                payroll.calculate_totals()
                payroll.save()
                messages.success(request, 'Payroll record updated.')
                return redirect('manage_payroll')
        else:
            # Adding new payroll
            form = PayrollForm(request.POST, company=request.user.company)
            if form.is_valid():
                payroll = form.save(commit=False)
                payroll.company = request.user.company
                payroll.calculate_totals()
                payroll.save()
                messages.success(request, 'Payroll record added.')
                return redirect('manage_payroll')
    else:
        form = PayrollForm(company=request.user.company)

    context = {
        'payrolls': payrolls,
        'form': form,
        'pay_items': pay_items,  # Always defined
    }
    return render(request, 'payroll_manage.html', context)


def delete_payroll(request, pk):
    payroll = get_object_or_404(Payroll, pk=pk)
    payroll.delete()
    messages.success(request, 'Payroll record deleted.')
    return redirect('manage_payroll')
from django.http import HttpResponse
from employee.models import SalaryAndStatutory
def generate_payslip(request, payroll_id):
    payroll = get_object_or_404(Payroll, id=payroll_id)
    employee = payroll.employee
    company = payroll.company

    # Get salary structure
    try:
        salary = SalaryAndStatutory.objects.get(employee=employee)
    except SalaryAndStatutory.DoesNotExist:
        salary = None

    # Get earnings and deductions
    all_items = PayItem.objects.filter(company=company)
    earnings = []
    deductions = []

    for item in all_items:
        if item.assign_to == 'all' or employee in item.specific_employees.all():
            if item.item_type == 'earning':
                earnings.append(item)
            elif item.item_type == 'deduction':
                deductions.append(item)

    context = {
        'payroll': payroll,
        'employee': employee,
        'company': company,
        'salary': salary,
        'earnings': earnings,
        'deductions': deductions,
    }

    return render(request, 'payslip_template.html',context)
