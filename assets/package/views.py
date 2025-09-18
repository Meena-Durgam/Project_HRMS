# views.py (company_owner app or shared views)

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Package, SubscribedCompany
from accounts.models import Company
from datetime import timedelta

@login_required
def company_subscription_page(request):
    company = request.user.company
    subscriptions = SubscribedCompany.objects.filter(company=company).select_related('package')

    for sub in subscriptions:
        if sub.package.plan_type == 'Monthly':
            sub.end_date = sub.subscribed_on + timedelta(days=30)
        elif sub.package.plan_type == 'Yearly':
            sub.end_date = sub.subscribed_on + timedelta(days=365)
        else:
            sub.end_date = None  # or set a default fallback



    monthly_plans = Package.objects.filter(plan_type='Monthly')
    yearly_plans = Package.objects.filter(plan_type='Yearly')

    for plan in monthly_plans:
        plan.module_items = plan.module_list.split(",") if plan.module_list else []

    for plan in yearly_plans:
        plan.module_items = plan.module_list.split(",") if plan.module_list else []

    current_subscription = SubscribedCompany.objects.filter(company=request.user.company).first()

    context = {
        'monthly_plans': monthly_plans,
        'yearly_plans': yearly_plans,
        'current_subscription': current_subscription,
        'subscriptions': subscriptions,
    }
    return render(request, 'subscription.html', context)


@login_required
def subscribe_to_package(request, plan_id):
    company = request.user.company
    package = get_object_or_404(Package, id=plan_id)

    # Optional: delete previous subscription
    SubscribedCompany.objects.filter(company=company).delete()

    SubscribedCompany.objects.create(company=company, package=package)
    return redirect('company_subscription_page')
