from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Designation
from .forms import DesignationForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.db import IntegrityError

from .forms import DesignationForm
from .models import Designation


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Designation
from .forms import DesignationForm


@login_required
def manage_designations(request):
    if request.user.role != 'company_owner':
        return render(request, 'unauthorized.html')

    company = request.user.company

    # --- Filtering ---
    search_name = request.GET.get('name', '').strip()
    search_status = request.GET.get('status', '').strip()
    search_department = request.GET.get('department', '').strip()

    designations = Designation.objects.filter(company=company).select_related('department')

    if search_name:
        designations = designations.filter(name__icontains=search_name)
    if search_status:
        designations = designations.filter(status=search_status)
    if search_department:
        designations = designations.filter(department__name__icontains=search_department)

    # --- Sorting ---
    sort_by = request.GET.get('sort', 'name')
    direction = request.GET.get('dir', 'asc')
    valid_sort_fields = {
        'name': 'name',
        'department': 'department__name',
        'status': 'status',
    }
    order_field = valid_sort_fields.get(sort_by, 'name')
    if direction == 'desc':
        order_field = f'-{order_field}'
    designations = designations.order_by(order_field)

    # --- Pagination (with per_page dropdown) ---
    try:
        per_page = int(request.GET.get('per_page', 5))
        if per_page not in [5, 10, 15, 20]:
            per_page = 5
    except ValueError:
        per_page = 5

    paginator = Paginator(designations, per_page)
    page = request.GET.get('page')

    try:
        designations_page = paginator.page(page)
    except PageNotAnInteger:
        designations_page = paginator.page(1)
    except EmptyPage:
        designations_page = paginator.page(paginator.num_pages)

    # --- Form Initialization ---
    form = DesignationForm(user=request.user)

    # --- POST Actions ---
    if request.method == 'POST':
        # --- ADD ---
        if 'add_designation' in request.POST:
            form = DesignationForm(request.POST, user=request.user)
            if form.is_valid():
                designation = form.save(commit=False)
                designation.company = company
                try:
                    designation.save()
                    messages.success(request, "Designation added successfully.")
                except IntegrityError:
                    messages.error(request, "Designation already exists.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
                for error in form.non_field_errors():
                    messages.error(request, error)
            return redirect('manage_designations')

        # --- EDIT ---
        elif 'edit_designation_id' in request.POST:
            designation = get_object_or_404(
                Designation,
                id=request.POST.get('edit_designation_id'),
                company=company
            )
            form = DesignationForm(request.POST, instance=designation, user=request.user)
            if form.is_valid():
                try:
                    form.save()
                    messages.success(request, "Designation updated successfully.")
                except IntegrityError:
                    messages.error(request, "Designation already exists.")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.capitalize()}: {error}")
                for error in form.non_field_errors():
                    messages.error(request, error)
            return redirect('manage_designations')

        # --- DELETE ---
        elif 'delete_designation_id' in request.POST:
            designation = get_object_or_404(
                Designation,
                id=request.POST.get('delete_designation_id'),
                company=company
            )
            designation.delete()
            messages.success(request, "Designation deleted successfully.")
            return redirect('manage_designations')

    # --- Context ---
    context = {
        'form': DesignationForm(user=request.user),
        'designations': designations_page,
        'sort_by': sort_by,
        'direction': direction,
        'search_name': search_name,
        'search_status': search_status,
        'search_department': search_department,
        'paginator': paginator,
        'per_page': per_page,
        'per_page_options': [5, 10, 15, 20],
        'show_add_modal': False,
    }

    return render(request, 'designation/manage_designations.html', context)


# views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Designation

def delete_designation(request, pk):
    if request.method == "POST":
        designation = get_object_or_404(Designation, pk=pk)
        designation.delete()
        messages.success(request, "Designation deleted successfully.")
    return redirect('manage_designations')  # change to your actual list view name
