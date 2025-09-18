from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Policy
from .forms import PolicyForm
from django.core.paginator import Paginator

@login_required
def manage_policies(request):
    company = request.user.company
    policies = Policy.objects.filter(company=company)
    name_query = request.GET.get('name')
    date_query = request.GET.get('created_at')

    if name_query:
        policies = policies.filter(name__icontains=name_query)

    if date_query:
        policies = policies.filter(created_at__date=date_query)

    # --- Page size handling (default = 5) ---
    try:
        page_size = int(request.GET.get('page_size', 5))  # default changed to 5
    except ValueError:
        page_size = 5

    paginator = Paginator(policies, page_size)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        policy_id = request.POST.get("delete_policy_id")
        if policy_id and request.user.role == 'company_owner':
            policy = get_object_or_404(Policy, id=policy_id, company=company)
            policy.delete()
            messages.success(request, "Policy deleted successfully.")
            return redirect('manage_policies')

    return render(request, 'policy_list.html', {
        'page_obj': page_obj,
        'total_entries': paginator.count,
        'page_size': page_size,
        'policies':policies,
    })


@login_required
def add_policy(request):
    if request.user.role != 'company_owner':
        messages.error(request, "Unauthorized access.")
        return redirect('manage_policies')

    if request.method == 'POST':
        form = PolicyForm(request.POST, request.FILES)
        if form.is_valid():
            policy = form.save(commit=False)
            policy.company = request.user.company
            policy.created_by = request.user
            policy.save()
            messages.success(request, "Policy added successfully.")
            return redirect('manage_policies')
    else:
        form = PolicyForm()
    return render(request, 'add_policy.html', {'form': form})

@login_required
def edit_policy(request, pk):
    company = request.user.company
    policy = get_object_or_404(Policy, pk=pk, company=company)

    if request.user.role != 'company_owner':
        messages.error(request, "Unauthorized access.")
        return redirect('manage_policies')

    if request.method == 'POST':
        form = PolicyForm(request.POST, request.FILES, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, "Policy updated successfully.")
            return redirect('manage_policies')
    else:
        form = PolicyForm(instance=policy)

    return render(request, 'add_policy.html', {'form': form, 'policy': policy})

@login_required
def delete_policy(request, pk):
    policy = get_object_or_404(Policy, pk=pk)
    policy.delete()
    messages.success(request, "Policy deleted successfully.")
    return redirect('manage_policies')

@login_required
def view_policy(request, pk):
    policy = get_object_or_404(Policy, pk=pk)
    return render(request, 'view_policy.html', {'policy': policy})
