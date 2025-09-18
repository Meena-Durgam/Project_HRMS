from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Asset
from .forms import AssetForm
from employee.models import Employee
from django.db.models import Q

@login_required
def asset_list(request):
    assets = Asset.objects.all().select_related('employee')
    employees = Employee.objects.filter(status='Active')

    # Filtering
    employee_username = request.GET.get('employee')
    status = request.GET.get('status')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if employee_username:
        assets = assets.filter(employee__id=employee_username)

    if status:
        assets = assets.filter(status=status)
    if start_date:
        assets = assets.filter(purchase_date__gte=start_date)
    if end_date:
        assets = assets.filter(purchase_date__lte=end_date)

    context = {
        'assets': assets,
        'employees': employees,
    }
    return render(request, 'assets.html', context)

@login_required
def add_asset(request):
    if request.method == 'POST':
        form = AssetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset added successfully.')
        else:
            print(form.errors)  # Add this line to see what's going wrong in the terminal
            messages.error(request, 'Asset form is not valid.')
        return redirect('asset_list')
    return redirect('asset_list')

@login_required
def edit_asset(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    if request.method == 'POST':
        form = AssetForm(request.POST, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asset updated successfully.')
            return redirect('asset_list')
    return redirect('asset_list')


@login_required
def delete_asset(request, asset_id):
    asset = get_object_or_404(Asset, id=asset_id)
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Asset deleted successfully.')
    return redirect('asset_list')