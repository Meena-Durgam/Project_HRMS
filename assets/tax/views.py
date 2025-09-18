from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Tax
from .forms import TaxForm
from notifications.utils import notify_roles


def tax_list(request):
    company = request.user.company  # Ensure your user model has company FK
    taxes = Tax.objects.filter(company=company).order_by('-id')
    form = TaxForm()

    if request.method == 'POST':
        if 'add_tax' in request.POST:
            form = TaxForm(request.POST)
            if form.is_valid():
                tax = form.save(commit=False)
                tax.company = company  # Assign current user's company
                tax.save()
                messages.success(request, 'Tax added successfully.')

                # ✅ Notify employees
                notify_roles(
                    roles=['employee'],
                    message=f"New tax '{tax.name}' was added by {request.user.username}.",
                    url='/tax/',  # update to your tax list URL
                    sender=request.user
                )
                return redirect('tax_list')

        elif 'edit_tax_id' in request.POST:
            tax_id = request.POST.get('edit_tax_id')
            tax = get_object_or_404(Tax, id=tax_id, company=company)
            form = TaxForm(request.POST, instance=tax)
            if form.is_valid():
                form.save()
                messages.success(request, 'Tax updated successfully.')
                # ✅ Notify employees
                notify_roles(
                    roles=['employee'],
                    message=f"Tax '{tax.name}' was updated by {request.user.username}.",
                    url='/tax/',
                    sender=request.user
                )
                return redirect('tax_list')

    return render(request, 'tax_list.html', {'taxes': taxes, 'form': form})


def delete_tax(request, tax_id):
    company = request.user.company
    tax = get_object_or_404(Tax, id=tax_id, company=company)
    tax_name = tax.name
    tax.delete()
    messages.success(request, 'Tax deleted successfully.')
    # ✅ Notify employees
    notify_roles(
        roles=['employee'],
        message=f"Tax '{tax_name}' was deleted by {request.user.username}.",
        url='/tax/',
        sender=request.user
    )
    return redirect('tax_list')


def change_tax_status(request, tax_id, new_status):
    company = request.user.company
    tax = get_object_or_404(Tax, id=tax_id, company=company)

    if new_status in ['Active', 'Inactive']:
        tax.status = new_status
        tax.save()
        messages.success(request, f"Tax status changed to {new_status}.")

        # ✅ Notify employees
        notify_roles(
            roles=['employee'],
            message=f"Tax '{tax.name}' status changed to {new_status} by {request.user.username}.",
            url='/tax/',
            sender=request.user
        )

    return redirect('tax_list')
