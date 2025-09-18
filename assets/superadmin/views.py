from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from package.models import Package
from django.contrib import messages
from accounts.models import Company
from collections import defaultdict
from django.db.models import Count
from django.utils import timezone
from django.utils.timezone import localtime 
from accounts.models import CustomUser
from django.db.models import Sum
from package.models import SubscribedCompany


# Optional: Check if user is a superadmin
def is_superadmin(user):
    return user.is_authenticated and user.role == 'superadmin'

@login_required
@user_passes_test(is_superadmin)

def superadmin_dashboard(request):
    companies = Company.objects.all()
    active_companies = companies.filter(is_active=True).count()
    total_subscribers = SubscribedCompany.objects.values('company').distinct().count()

    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)          # Sunday

    # ✅ Companies registered this week
    weekly_companies = Company.objects.filter(created_at_date_range=(start_of_week, end_of_week))
    
    company_by_day = defaultdict(int)
    company_names_by_day = defaultdict(list)

    for company in weekly_companies:
        created_day = localtime(company.created_at).strftime('%a')  # 'Mon', 'Tue', etc.
        company_by_day[created_day] += 1
        company_names_by_day[created_day].append(company.name)

    bar_chart_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    bar_chart_data = [company_by_day.get(day, 0) for day in bar_chart_labels]
    company_names_tooltip = [", ".join(company_names_by_day.get(day, [])) for day in bar_chart_labels]
    registered_this_week = sum(bar_chart_data)

    # ✅ Plan distribution (Top 5 packages)
    plan_distribution = (
        SubscribedCompany.objects
        .values('package__name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )

    pie_chart_labels = [entry['package__name'] for entry in plan_distribution]
    pie_chart_data = [entry['count'] for entry in plan_distribution]

    # ✅ Monthly plans (for some other card)
    monthly_plans = Package.objects.filter(plan_type='Monthly')
    for plan in monthly_plans:
        plan.module_items = plan.module_list.split(",") if plan.module_list else []

    # ✅ Recently Registered Companies (last 5)
    recent_registered = companies.order_by('-created_at')[:5]

    # ✅ Recently Expired Subscriptions (last 5)
    # recently_expired = SubscribedCompany.objects.filter(
     #   expiry_date__lt=timezone.now()
    #).order_by('-expiry_date')[:5]

    # ✅ New companies today
    new_companies_today = companies.filter(created_at__date=today).count()

    # Debug
    print("=== Dashboard Debug ===")
    print("Total Companies:", companies.count())
    print("Active Companies:", active_companies)
    print("Total Subscribers:", total_subscribers)
    print("Registered This Week:", registered_this_week)

    context = {
        'companies': companies,
        'active_companies': active_companies,
        'total_subscribers': total_subscribers,
        'monthly_plans': monthly_plans,
        'new_companies_today': new_companies_today,
        'registered_this_week': registered_this_week,
        'bar_chart_labels': bar_chart_labels,
        'bar_chart_data': bar_chart_data,
        'company_names_tooltip': company_names_tooltip,
        'pie_chart_labels': pie_chart_labels,
        'pie_chart_data': pie_chart_data,
        'recent_registered': recent_registered,
        
    }

    return render(request, 'dashboard/superadmin_dashboard.html', context)



from django.db.models import Count

@login_required
@user_passes_test(is_superadmin)
def company_list_view(request):
    companies = Company.objects.all()

    # Count totals
    total_companies = companies.count()
    active_companies = companies.filter(is_active=True).count()
    inactive_companies = companies.filter(is_active=False).count()

    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    status = request.GET.get('status')
    sort = request.GET.get('sort')
    search = request.GET.get('search')

    # Filter by date range
    if start_date and end_date:
        companies = companies.filter(created_at_date_range=[start_date, end_date])

    # Filter by active status
    if status == 'active':
        companies = companies.filter(is_active=True)
    elif status == 'inactive':
        companies = companies.filter(is_active=False)

    # Search by company name
    if search:
        companies = companies.filter(name__icontains=search)

    # Sorting
    if sort == 'latest':
        companies = companies.order_by('-created_at')
    elif sort == 'oldest':
        companies = companies.order_by('created_at')

    context = {
        'companies': companies,
        'total_companies': total_companies,
        'active_companies': active_companies,
        'inactive_companies': inactive_companies,
        'start_date': start_date,
        'end_date': end_date,
        'status': status,
        'sort': sort,
        'search': search,
    }
    return render(request, 'dashboard/company_list.html', context)



from django.db.models import Q
from django.utils.dateparse import parse_date

@login_required
@user_passes_test(is_superadmin)
def subscription_package_view(request):
    # Handle form submission (adding a new plan)
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        plan_type = request.POST.get('plan_type')
        number_of_users = request.POST.get('number_of_users')
        number_of_projects = request.POST.get('number_of_projects')
        storage_space = request.POST.get('storage_space')
        description = request.POST.get('description')
        status = True if request.POST.get('status') == '1' else False
        modified_date = request.POST.get('modified_date')
        parsed_modified_date = parse_date(modified_date) if modified_date else None

        Package.objects.create(
            name=name,
            amount=amount,
            plan_type=plan_type,
            number_of_users=number_of_users,
            number_of_projects=number_of_projects,
            storage_space=storage_space,
            description=description,
            status=status,
            modified_date=parsed_modified_date
        )

        messages.success(request, "Plan added successfully.")
        return redirect('package_list')

    # Handle filters from GET
    filter_date = request.GET.get('date')
    filter_plan_type = request.GET.get('plan_type')
    filter_status = request.GET.get('status')
    sort_by = request.GET.get('sort_by')

    # Start with all plans
    plans = Package.objects.all()

    # Apply filters
    if filter_date:
        parsed_date = parse_date(filter_date)
        if parsed_date:
            plans = plans.filter(created_date__date=parsed_date)

    if filter_plan_type and filter_plan_type != "Select Plan":
        plans = plans.filter(plan_type__iexact=filter_plan_type)

    if filter_status == "active":
        plans = plans.filter(status=True)
    elif filter_status == "inactive":
        plans = plans.filter(status=False)

    # Sorting
    if sort_by == "latest":
        plans = plans.order_by('-created_date')

    elif sort_by == "oldest":
        plans = plans.order_by('-created_date')


    context = {
        'plans': plans,
        'total_plans': plans.count(),
        'active_plans': plans.filter(status=True).count(),
        'inactive_plans': plans.filter(status=False).count(),
        'plan_types': Package.objects.values('plan_type').distinct().count(),
        'plan_type_choices': ['Monthly', 'Yearly'],

        # To preserve filter values in the template
        'filter_date': filter_date,
        'filter_plan_type': filter_plan_type,
        'filter_status': filter_status,
        'sort_by': sort_by,
    }

    return render(request, 'dashboard/subscription_packages.html', context)


@login_required
@user_passes_test(is_superadmin)
def edit_plan(request, plan_id):
    plan = get_object_or_404(Package, id=plan_id)
    if request.method == 'POST':
        plan.name = request.POST.get('name')
        plan.amount = request.POST.get('amount')
        plan.plan_type = request.POST.get('plan_type')
        plan.number_of_users = request.POST.get('number_of_users')
        plan.number_of_projects = request.POST.get('number_of_projects')
        plan.storage_space = request.POST.get('storage_space')
        plan.description = request.POST.get('description')
        plan.status = True if request.POST.get('status') == '1' else False

        modified_date = request.POST.get('modified_date')
        plan.modified_date = parse_date(modified_date) if modified_date else None

        plan.save()
        messages.success(request, "Plan updated successfully.")
        return redirect('package_list')

    return redirect('package_list')


@login_required
@user_passes_test(is_superadmin)
def delete_plan(request, plan_id):
    plan = get_object_or_404(Package, id=plan_id)
    if request.method == 'POST':
        plan_name = plan.name
        plan.delete()
        messages.success(request, f"Plan deleted successfully.")
    return redirect('package_list')

@login_required
@user_passes_test(is_superadmin)
def domain_purchase_view(request):
    return render(request, 'dashboard/domain_purchases.html')

@login_required
@user_passes_test(is_superadmin)
def transaction_list_view(request):
    return render(request, 'dashboard/transactions.html')


# superadmin/views.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import timedelta, datetime
from django.db.models import Q
from package.models import SubscribedCompany
from accounts.models import Company

@login_required
def subscribed_companies_list(request):
    subscribed_companies = SubscribedCompany.objects.select_related('company', 'package')
    subscriptions = SubscribedCompany.objects.select_related('company', 'package')

    # 🔍 Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    selected_plan = request.GET.get('plan')
    sort_by = request.GET.get('sort_by')

    if start_date:
        subscriptions = subscriptions.filter(subscribed_on_date_gte=start_date)
    if end_date:
        subscriptions = subscriptions.filter(subscribed_on_date_lte=end_date)
    if selected_plan:
        subscriptions = subscriptions.filter(package_name_icontains=selected_plan)
    if sort_by == 'latest':
        subscriptions = subscriptions.order_by('-subscribed_on')
    elif sort_by == 'oldest':
        subscriptions = subscriptions.order_by('subscribed_on')

    # 💡 Calculate end_date
    for sub in subscriptions:
        if sub.package.plan_type == 'Monthly':
            sub.end_date = sub.subscribed_on + timedelta(days=30)
        elif sub.package.plan_type == 'Yearly':
            sub.end_date = sub.subscribed_on + timedelta(days=365)
        else:
            sub.end_date = None

    # 📊 Card counts
    total_subscribers = subscriptions.count()
    active_subscribers = sum(1 for sub in subscriptions if sub.end_date and sub.end_date >= timezone.now())
    inactive_subscribers = total_subscribers - active_subscribers

    # 📌 Plan choices
    all_plans = Package.objects.values_list('name', flat=True).distinct()

    # Add calculated end date for display
    for sub in subscribed_companies:
        if sub.package.plan_type == 'Monthly':
            sub.end_date = sub.subscribed_on + timedelta(days=30)
        elif sub.package.plan_type == 'Yearly':
            sub.end_date = sub.subscribed_on + timedelta(days=365)
        else:
            sub.end_date = None

    context = {
        'subscribed_companies': subscribed_companies,
        'total_subscribers': total_subscribers,
        'active_subscribers': active_subscribers,
        'inactive_subscribers': inactive_subscribers,
        'plan_choices': all_plans,
        'filter_start_date': start_date,
        'filter_end_date': end_date,
        'filter_plan': selected_plan,
        'filter_sort': sort_by,

    }
    return render(request, 'dashboard/subscribed_companies.html',context)