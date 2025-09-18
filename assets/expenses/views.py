from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm
from django.core.paginator import Paginator
from django.contrib import messages

from django.db.models import Q
from django.utils.dateparse import parse_date

def expense_list(request):
    # Base queryset filtered by logged-in user's company
    expenses_qs = Expense.objects.filter(company=request.user.company).order_by('expense_id')

    # Get filter params
    search = request.GET.get('search', '').strip()
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    category = request.GET.get('category', '').strip()
    status = request.GET.get('status', '').strip()

    # Apply filters
    if search:
        expenses_qs = expenses_qs.filter(
            Q(expense_id__icontains=search) | Q(expense_title__icontains=search)
        )
    if from_date:
        expenses_qs = expenses_qs.filter(expense_date__gte=from_date)
    if to_date:
        expenses_qs = expenses_qs.filter(expense_date__lte=to_date)
    if category:
        expenses_qs = expenses_qs.filter(category=category)
    if status:
        expenses_qs = expenses_qs.filter(status=status)

    # Pagination settings
    try:
        page_size = int(request.GET.get('per_page', 5))
        if page_size <= 0:
            page_size = 5
    except ValueError:
        page_size = 5

    paginator = Paginator(expenses_qs, page_size)

    try:
        page_number = int(request.GET.get('page', 1))
        page_obj = paginator.page(page_number)
    except Exception:
        page_obj = paginator.page(1)

    # Create edit forms only for expenses in current page
    edit_forms = {expense.id: ExpenseForm(instance=expense) for expense in page_obj}

    # Categories for dropdown - distinct categories of current company
    categories = Expense.objects.filter(company=request.user.company).values_list('category', flat=True).distinct()

    # Add Expense form for modal
    form = ExpenseForm()

    # Handle add expense POST
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            new_expense = form.save(commit=False)
            new_expense.company = request.user.company
            new_expense.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('expense_list')
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'expenses': page_obj,       # paginated expenses
        'form': form,               # add expense form
        'categories': categories,
        'edit_forms': edit_forms,
        'page_size': page_size,
    }
    return render(request, 'expenses.html', context)



from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
        else:
            messages.error(request, 'Failed to update expense. Please check the form.')
    return redirect('expense_list')


def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'Expense deleted successfully.')
    else:
        messages.error(request, 'Invalid request method for deleting expense.')
    return redirect('expense_list')



