from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.contrib import messages
from .models import Estimate, EstimateItem
from .forms import EstimateForm, EstimateItemForm
# ✅ HR Check
from .utils import is_hr_user
from datetime import datetime

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# ✅ Estimate List (open to all)
def estimate_list(request):
    company = None
    try:
        if hasattr(request.user, 'employee_account'):
            company = request.user.employee_account.company
        elif getattr(request.user, 'role', '').lower() == 'company_owner' and hasattr(request.user, 'company'):
            company = request.user.company

        if company:
            estimates = Estimate.objects.filter(company=company).order_by('created_at')
        else:
            estimates = Estimate.objects.none()
    except Exception as e:
        messages.error(request, f"Error fetching estimates: {str(e)}")
        estimates = Estimate.objects.none()

    # Filters
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    status = request.GET.get('status')
    estimate_number = request.GET.get('estimate_number')
    client_name = request.GET.get('client_name')

    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, "%d/%m/%Y")
            estimates = estimates.filter(estimate_date__gte=from_date_obj)
        except ValueError:
            messages.error(request, "Invalid 'From' date format.")

    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, "%d/%m/%Y")
            estimates = estimates.filter(estimate_date__lte=to_date_obj)
        except ValueError:
            messages.error(request, "Invalid 'To' date format.")

    if status:
        estimates = estimates.filter(status=status)

    if estimate_number:
        estimates = estimates.filter(estimate_number__icontains=estimate_number)

# ✅ Correct usage of client__client_name
    if client_name:
        estimates = estimates.filter(client__client_name__icontains=client_name)

    # ✅ Pagination (8 per page)
    paginator = Paginator(estimates, 8)
    page = request.GET.get('page')
    try:
        estimates_page = paginator.page(page)
    except PageNotAnInteger:
        estimates_page = paginator.page(1)
    except EmptyPage:
        estimates_page = paginator.page(paginator.num_pages)

    return render(request, 'estimates.html', {
        'estimates': estimates_page,
        'paginator': paginator,
    })



def estimate_list_create(request):
    if not is_hr_user(request.user):
        messages.error(request, "Only Human Resources department employees or company owners can create estimates.")
        return redirect('estimate_list')

    EstimateItemFormSet = modelformset_factory(EstimateItem, form=EstimateItemForm, extra=1)

    if request.method == 'POST':
        estimate_form = EstimateForm(request.POST, user=request.user)
        item_formset = EstimateItemFormSet(request.POST)

        if estimate_form.is_valid() and item_formset.is_valid():
            estimate = estimate_form.save(commit=False)

            # ✅ Try to get company from employee or directly for company_owner
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
                return redirect('estimate_list')

            estimate.company = company
            estimate.save()  # triggers generate_estimate_number and save

            # Save item formset
            for item_form in item_formset:
                if item_form.cleaned_data:
                    item = item_form.save(commit=False)
                    item.estimate = estimate
                    item.save()

            # Recalculate totals and save
            estimate.calculate_totals()
            estimate.save(update_fields=['total_amount', 'tax_amount', 'grand_total'])

            messages.success(request, "Estimate created successfully!")
            return redirect('estimate_list')

        messages.error(request, "There was an error creating the estimate.")
    else:
        estimate_form = EstimateForm(user=request.user)
        item_formset = EstimateItemFormSet(queryset=EstimateItem.objects.none())

    return render(request, 'create_estimate.html', {
        'estimate_form': estimate_form,
        'item_formset': item_formset,
    })
from django.http import JsonResponse
from projects.models import Project
from clients.models import Client

from django.contrib.auth.decorators import login_required
@login_required
def get_projects_by_client(request):
    client_id = request.GET.get('client_id')
    user = request.user
    company = request.user.company

    if not client_id or not company:
        return JsonResponse({'error': 'Invalid data'}, status=400)

    projects = Project.objects.filter(client__id=client_id, company=company).values('id', 'name')
    return JsonResponse(list(projects), safe=False)

# ✅ Update Estimate (HR only)
from django.http import Http404

def estimate_update(request, pk):
    if not is_hr_user(request.user) and request.user.role != 'company_owner':
        messages.error(request, "Only Human Resources department employees or company owners can update estimates.")
        return redirect('estimate_list')

    # Get the company from either HR user or company owner
    company = None
    try:
        if hasattr(request.user, 'employee_account'):
            company = request.user.employee_account.company
        elif request.user.role == 'company_owner' and hasattr(request.user, 'company'):
            company = request.user.company
    except Exception:
        pass

    if not company:
        messages.error(request, "Your account is not linked to any company.")
        return redirect('estimate_list')

    # Only allow editing estimates that belong to the user's company
    estimate = get_object_or_404(Estimate, pk=pk, company=company)

    EstimateItemFormSet = modelformset_factory(EstimateItem, form=EstimateItemForm, extra=0, can_delete=True)

    if request.method == 'POST':
        estimate_form = EstimateForm(request.POST, instance=estimate, user=request.user)
        item_formset = EstimateItemFormSet(request.POST, queryset=estimate.items.all())

        if estimate_form.is_valid() and item_formset.is_valid():
            estimate = estimate_form.save(commit=False)
            estimate.company = company  # Reassign company just in case
            estimate.save()

            for form in item_formset:
                if form.cleaned_data:
                    if form.cleaned_data.get('DELETE') and form.instance.pk:
                        form.instance.delete()
                    else:
                        item = form.save(commit=False)
                        item.estimate = estimate
                        item.save()

            estimate.calculate_totals()
            estimate.save(update_fields=['total_amount', 'tax_amount', 'grand_total'])

            messages.success(request, "Estimate updated successfully!")
            return redirect('estimate_list')

        # Show form errors
        for field, errors in estimate_form.errors.items():
            for error in errors:
                messages.error(request, f"{field.capitalize()}: {error}")
        for error in estimate_form.non_field_errors():
            messages.error(request, error)
        for form in item_formset:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

    else:
        estimate_form = EstimateForm(instance=estimate, user=request.user)
        item_formset = EstimateItemFormSet(queryset=estimate.items.all())

    return render(request, 'create_estimate.html', {
        'estimate_form': estimate_form,
        'item_formset': item_formset,
        'is_update': True,
        'estimate_id': estimate.id,
    })
# ✅ View Estimate (open to all)
def estimate_detail(request, pk):
    company = None
    try:
        if hasattr(request.user, 'employee_account'):
            company = request.user.employee_account.company
        elif request.user.role == 'company_owner' and hasattr(request.user, 'company'):
            company = request.user.company
    except Exception:
        pass

    if not company:
        messages.error(request, "You are not linked to any company.")
        return redirect('estimate_list')

    # Ensure the estimate belongs to the same company
    estimate = get_object_or_404(Estimate, pk=pk, company=company)
    items = estimate.items.all()

    return render(request, 'estimate_detail.html', {
        'estimate': estimate,
        'items': items,
    })

# ✅ Delete Estimate (HR only)
def estimate_delete(request, pk):
    if not is_hr_user(request.user) and request.user.role != 'company_owner':
        messages.error(request, "Only Human Resources department employees or company owners can delete estimates.")
        return redirect('estimate_list')

    company = None
    try:
        if hasattr(request.user, 'employee_account'):
            company = request.user.employee_account.company
        elif request.user.role == 'company_owner' and hasattr(request.user, 'company'):
            company = request.user.company
    except Exception:
        pass

    if not company:
        messages.error(request, "Your account is not linked to any company.")
        return redirect('estimate_list')

    estimate = get_object_or_404(Estimate, pk=pk, company=company)
    estimate.delete()
    messages.success(request, "Estimate deleted successfully!")
    return redirect('estimate_list')
