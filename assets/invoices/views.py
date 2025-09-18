from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.dateparse import parse_date
from datetime import datetime

from .models import Invoice, InvoiceItem
from .forms import InvoiceForm, InvoiceItemForm
from tax.models import Tax
from projects.models import Project
from estimate.models import Estimate

# ✅ Utility functions
def is_finance_or_hr_user(user):
    try:
        if getattr(user, 'role', '').strip().lower() == 'company_owner':
            return True
        if hasattr(user, 'employee_account') and user.employee_account.department:
            department_name = user.employee_account.department.name.strip().lower()
            return department_name in ['finance', 'human resources']
    except Exception:
        pass
    return False

def is_company_or_finance_or_hr_user(user):
    return user.role in ['company_owner', 'finance', 'hr']

def get_company_from_user(user):
    try:
        if hasattr(user, 'company') and user.company:
            return user.company
        if hasattr(user, 'employee_account') and user.employee_account.company:
            return user.employee_account.company
    except Exception:
        pass
    return None

# ✅ List invoices (filtered by user's company and optional filters)
def invoice_list(request):
    if not is_company_or_finance_or_hr_user(request.user):
        messages.error(request, "Only Company Owners, HR, or Finance employees can view invoices.")
        return redirect('home')

    company = get_company_from_user(request.user)
    invoices = Invoice.objects.filter(client__company=company).order_by('created_at')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    status = request.GET.get('status')

    if from_date:
        invoices = invoices.filter(invoice_date__gte=parse_date(from_date))
    if to_date:
        invoices = invoices.filter(invoice_date__lte=parse_date(to_date))
    if status:
        invoices = invoices.filter(status=status)

    return render(request, 'invoices.html', {'invoices': invoices})

# ✅ View single invoice
def invoice_detail(request, pk):
    company = get_company_from_user(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, client__company=company)
    items = invoice.items.all()
    return render(request, 'invoice_detail.html', {'invoice': invoice, 'items': items})
from django.forms import modelformset_factory
from django.db import transaction
from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from .models import Invoice, InvoiceItem, Tax


# ✅ Create invoice
def invoice_create(request):
    if not is_company_or_finance_or_hr_user(request.user):
        messages.error(request, "Only Finance, HR employees, or Company Owners can create invoices.")
        return redirect('invoice_list')

    InvoiceItemFormSet = modelformset_factory(InvoiceItem, form=InvoiceItemForm, extra=1, can_delete=True)

    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST, user=request.user)
        item_formset = InvoiceItemFormSet(request.POST, queryset=InvoiceItem.objects.none())

        if invoice_form.is_valid() and item_formset.is_valid():
            invoice = invoice_form.save(commit=False)

            # ✅ Assign company
            company = None
            try:
                if hasattr(request.user, 'employee_account'):
                    company = request.user.employee_account.company
                elif getattr(request.user, 'role', '').lower() == 'company_owner' and hasattr(request.user, 'company'):
                    company = request.user.company
            except Exception:
                pass

            if not company:
                messages.error(request, "Your account is not linked to any company.")
                return redirect('invoice_list')

            invoice.company = company
            invoice.save()  # triggers generate_invoice_number and save

            # Save items
            for item_form in item_formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    item = item_form.save(commit=False)
                    item.invoice = invoice
                    item.save()

            # Recalculate totals
            invoice.calculate_totals()
            invoice.save(update_fields=['total_amount', 'tax_amount', 'grand_total'])

            messages.success(request, "Invoice created successfully!")
            return redirect('invoice_list')

        messages.error(request, "There was an error creating the invoice.")
    else:
        invoice_form = InvoiceForm(user=request.user)
        item_formset = InvoiceItemFormSet(queryset=InvoiceItem.objects.none())

    return render(request, 'invoice_form.html', {
        'invoice_form': invoice_form,
        'item_formset': item_formset,
    })

# ✅ Update invoice
def invoice_update(request, pk):
    if not is_company_or_finance_or_hr_user(request.user):
        messages.error(request, "Only Finance, HR employees, or Company Owners can update invoices.")
        return redirect('invoice_list')

    company = get_company_from_user(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, client__company=company)

    InvoiceItemFormSet = modelformset_factory(
        InvoiceItem,
        form=InvoiceItemForm,
        extra=0,
        can_delete=True
    )

    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST, instance=invoice, user=request.user)
        item_formset = InvoiceItemFormSet(request.POST, queryset=InvoiceItem.objects.filter(invoice=invoice))

        invoice_valid = invoice_form.is_valid()
        formset_valid = item_formset.is_valid()

        # Ensure at least one item
        has_item = any(
            form.cleaned_data and not form.cleaned_data.get('DELETE')
            for form in item_formset.forms if hasattr(form, 'cleaned_data')
        )
        if not has_item:
            formset_valid = False
            messages.error(request, "Please keep at least one invoice item.")

        if invoice_valid and formset_valid:
            try:
                with transaction.atomic():
                    invoice = invoice_form.save()

                    for form in item_formset:
                        if form.cleaned_data:
                            if form.cleaned_data.get('DELETE') and form.instance.pk:
                                form.instance.delete()
                            else:
                                item = form.save(commit=False)
                                item.invoice = invoice
                                item.save()

                    invoice.calculate_totals()
                    invoice.save()

                    messages.success(request, "Invoice updated successfully.")
                    return redirect('invoice_list')
            except Exception as e:
                messages.error(request, f"Error updating invoice: {e}")
        else:
            for field, errors in invoice_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

            for idx, form in enumerate(item_formset.forms, start=1):
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Item {idx} - {field.capitalize()}: {error}")

    else:
        invoice_form = InvoiceForm(instance=invoice, user=request.user)
        item_formset = InvoiceItemFormSet(queryset=InvoiceItem.objects.filter(invoice=invoice))

    taxes = Tax.objects.filter(company=company, status='Active')

    return render(request, "invoice_form.html", {
        'invoice_form': invoice_form,
        'item_formset': item_formset,
        'taxes': taxes,
        'is_update': True,
        'invoice_id': invoice.pk,
    })


# ✅ Delete invoice
def invoice_delete(request, pk):
    if not is_company_or_finance_or_hr_user(request.user):
        messages.error(request, "Only Finance, HR employees, or Company Owners can delete invoices.")
        return redirect('invoice_list')

    company = get_company_from_user(request.user)
    invoice = get_object_or_404(Invoice, pk=pk, client__company=company)
    invoice.delete()

    messages.success(request, "Invoice deleted successfully.")
    return redirect('invoice_list')

# ✅ AJAX: Load projects and estimates based on client
def load_projects_estimates(request):
    client_id = request.GET.get('client_id')
    projects = Project.objects.filter(client_id=client_id).values('id', 'name')
    estimates = Estimate.objects.filter(client_id=client_id).values('id', 'estimate_number')
    return JsonResponse({
        'projects': list(projects),
        'estimates': list(estimates)
    })

# ✅ List paid invoices

def invoice_payments(request):
    company = request.user.company
    invoices = Invoice.objects.filter(client__company=company, status='Paid').order_by('created_at')

    invoice_number = request.GET.get('invoice_number', '').strip()
    client_name = request.GET.get('client_name', '').strip()
    invoice_date = request.GET.get('invoice_date', '').strip()

    if invoice_number:
        invoices = invoices.filter(invoice_number__icontains=invoice_number)
    if client_name:
        invoices = invoices.filter(client__client_name__icontains=client_name)
    if invoice_date:
        try:
            parsed_date = datetime.strptime(invoice_date, "%d-%m-%Y").date()
            invoices = invoices.filter(invoice_date=parsed_date)
        except ValueError:
            messages.error(request, "Invalid date format. Use DD-MM-YYYY.")

    page = request.GET.get('page', 1)
    paginator = Paginator(invoices, 10)

    try:
        invoices_page = paginator.page(page)
    except PageNotAnInteger:
        invoices_page = paginator.page(1)
    except EmptyPage:
        invoices_page = paginator.page(paginator.num_pages)

    return render(request, 'invoicespayments.html', {
        'invoices': invoices_page,
        'paginator': paginator,
    })

# ✅ Invoice Report
def invoice_report_view(request):
    invoices = Invoice.objects.all()

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')

    if start_date:
        invoices = invoices.filter(invoice_date__gte=start_date)
    if end_date:
        invoices = invoices.filter(invoice_date__lte=end_date)
    if status:
        invoices = invoices.filter(status=status)

    return render(request, 'invoice_report.html', {'invoices': invoices})
