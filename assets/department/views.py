from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Department
from .forms import DepartmentForm
from notifications.utils import notify_roles

@login_required
def manage_departments(request):
    add_form = DepartmentForm()
    edit_form = None

    # ✅ Handle Add
    if request.method == 'POST' and 'add_department' in request.POST:
        add_form = DepartmentForm(request.POST)
        if add_form.is_valid():
            name = add_form.cleaned_data['name']
            if Department.objects.filter(name__iexact=name.strip(), company=request.user.company).exists():
                messages.error(request, f"Department already exists.")
            else:
                department = add_form.save(commit=False)
                department.company = request.user.company
                department.save()
                messages.success(request, "Department added successfully.")

                notify_roles(
                    roles=['employee'],
                    message=f"A new department '{department.name}' was added by {request.user.get_full_name()}.",
                    url='/department/',
                    sender=request.user
                )
                return redirect('manage_departments')

    # ✅ Handle Edit
    if request.method == 'POST' and 'edit_department_id' in request.POST:
        dept_id = request.POST.get('edit_department_id')
        department = get_object_or_404(Department, id=dept_id, company=request.user.company)
        edit_form = DepartmentForm(request.POST, instance=department)
        if edit_form.is_valid():
            name = edit_form.cleaned_data['name']
            if Department.objects.filter(name__iexact=name.strip(), company=request.user.company).exclude(id=department.id).exists():
                messages.error(request, f"Another department with name '{name}' already exists.")
            else:
                edit_form.save()
                messages.success(request, "Department updated successfully.")

                notify_roles(
                    roles=['employee'],
                    message=f"Department '{department.name}' was updated by {request.user.get_full_name()}.",
                    url='/department/',
                    sender=request.user
                )
                return redirect('manage_departments')

    # ✅ Handle Delete
    if request.method == 'POST' and 'delete_department_id' in request.POST:
        dept_id = request.POST.get('delete_department_id')
        department = get_object_or_404(Department, id=dept_id, company=request.user.company)
        department_name = department.name
        department.delete()
        messages.success(request, "Department deleted successfully.")

        notify_roles(
            roles=['employee'],
            message=f"Department '{department_name}' was deleted by {request.user.get_full_name()}.",
            url='/department/',
            sender=request.user
        )
        return redirect('manage_departments')

    # ✅ Filtering and Sorting
    departments = Department.objects.filter(company=request.user.company)

    search_name = request.GET.get('name', '')
    search_status = request.GET.get('status', '')
    sort = request.GET.get('sort', '')

    if search_name:
        departments = departments.filter(name__icontains=search_name.strip())
    if search_status:
        departments = departments.filter(status=search_status)

    if sort == 'name_asc':
        departments = departments.order_by('name')
    elif sort == 'name_desc':
        departments = departments.order_by('-name')
    elif sort == 'recent':
        departments = departments.order_by('-id')
    else:
        departments = departments.order_by('id')  # Default sort

    # ✅ Pagination
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 5)

    try:
        page_size = int(page_size)
        if page_size <= 0:
            page_size = 5
    except ValueError:
        page_size = 5

    paginator = Paginator(departments, page_size)

    try:
        departments_page = paginator.page(page)
    except PageNotAnInteger:
        departments_page = paginator.page(1)
    except EmptyPage:
        departments_page = paginator.page(paginator.num_pages)

    return render(request, 'department/manage_departments.html', {
        'departments': departments_page,
        'add_form': add_form,
        'edit_form': edit_form,
        'paginator': paginator,
        'page_size': page_size,
        'search_name': search_name,
        'search_status': search_status,
    })


from django.shortcuts import redirect, get_object_or_404
from .models import Department
from django.contrib import messages

def delete_department(request, pk):
    if request.method == 'POST':
        department = get_object_or_404(Department, pk=pk, company=request.user.company)
        department.delete()
        messages.success(request, 'Department deleted successfully.')
    return redirect('manage_departments')
