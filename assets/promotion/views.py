from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Promotion
from .forms import PromotionForm
from notifications.utils import notify_roles


@login_required
def promotion_list(request):
    company = request.user.company
    user_role = request.user.role

    promotions = Promotion.objects.filter(company=company)

    promotion_forms = {
        promotion.id: PromotionForm(instance=promotion, user=request.user)  # ✅ use user=...
        for promotion in promotions
    }

    add_form = PromotionForm(user=request.user)  # ✅ not company=

    return render(request, 'promotion.html', {
        'promotions': promotions,
        'user_role': user_role,
        'promotion_forms': promotion_forms,
        'promotion_form': add_form,
    })



@login_required
def promotion_add(request):
    company = request.user.company
    user_role = request.user.role

    if request.method == 'POST':
        form = PromotionForm(request.POST, user=request.user)  # ✅ FIXED HERE
        if form.is_valid():
            promotion = form.save(commit=False)
            employee = form.cleaned_data['employee']
            new_department = form.cleaned_data['new_department']
            new_designation = form.cleaned_data['new_designation']

            # Assign promotion details
            promotion.company = company
            promotion.old_department = employee.department
            promotion.old_designation = employee.designation
            promotion.created_by = request.user
            promotion.save()

            # Update employee's current department & designation
            employee.department = new_department
            employee.designation = new_designation
            employee.save()

            messages.success(request, "Promotion added successfully.")

            # ✅ Notify employees about promotion
            notify_roles(
                roles=['employee'],
                message=f"{employee.first_name} {employee.last_name} was promoted by {request.user.username}.",
                url='/promotions/',
                sender=request.user
            )
            return redirect('promotion_list')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = PromotionForm(user=request.user)

    return render(request, 'promotion.html', {
        'form': form,
        'title': 'Add Promotion',
        'user_role': user_role
    })


@login_required
def promotion_edit(request, pk):
    company = request.user.company
    user_role = request.user.role

    promotion = get_object_or_404(Promotion, pk=pk, company=company)

    if request.method == 'POST':
        form = PromotionForm(request.POST, instance=promotion, user=request.user)
        if form.is_valid():
            promotion = form.save(commit=False)
            employee = form.cleaned_data['employee']
            new_department = form.cleaned_data['new_department']
            new_designation = form.cleaned_data['new_designation']

            promotion.old_department = employee.department
            promotion.old_designation = employee.designation
            promotion.company = company
            promotion.created_by = request.user
            promotion.save()

            # Update employee's department/designation
            employee.department = new_department
            employee.designation = new_designation
            employee.save()

            messages.success(request, "Promotion updated successfully.")

            # ✅ Notify about promotion update
            notify_roles(
                roles=['employee'],
                message=f"Promotion for {employee.first_name} {employee.last_name} was updated by {request.user.username}.",
                url='/promotions/',
                sender=request.user
            )
            return redirect('promotion_list')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = PromotionForm(instance=promotion, company=company)

    return render(request, 'promotion.html', {
        'form': form,
        'title': 'Edit Promotion',
        'user_role': user_role
    })


@login_required
def promotion_delete(request, pk):
    company = request.user.company
    promotion = get_object_or_404(Promotion, pk=pk, company=company)
    employee_name = f"{promotion.employee.first_name} {promotion.employee.last_name}"
    promotion.delete()
    messages.success(request, "Promotion deleted successfully.")
    # ✅ Notify about deletion
    notify_roles(
        roles=['employee'],
        message=f"Promotion for {employee_name} was deleted by {request.user.username}.",
        url='/promotions/',
        sender=request.user
    )
    return redirect('promotion_list')
