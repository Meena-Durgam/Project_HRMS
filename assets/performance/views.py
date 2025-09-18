from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PerformanceIndicator, PerformanceAppraisal
from .forms import PerformanceIndicatorForm, PerformanceAppraisalForm
from .constants import TECH_FIELDS, ORG_FIELDS, TECH_COMPETENCIES, ORG_COMPETENCIES
from employee.models import Employee

# ======= INDICATOR VIEWS =======

@login_required
def performance_indicator_list(request):
    company = request.user.company
    indicators = PerformanceIndicator.objects.filter(company=company)

    performance_forms = {
        ind.id: PerformanceIndicatorForm(instance=ind, company=company)
        for ind in indicators
    }

    add_form = PerformanceIndicatorForm(company=company)

    # Prepare fields for template
    technical_fields = [add_form[field] for field in [
        "customer_experience", "marketing", "management",
        "administration", "presentation_skill", "quality_of_work"
    ]]
    organizational_fields = [add_form[field] for field in [
        "efficiency", "integrity", "professionalism",
        "teamwork", "critical_thinking", "conflict_management"
    ]]
    behavioral_fields = [add_form[field] for field in [
        "attendance", "punctuality", "dependability",
        "communication", "decision_making"
    ]]

    context = {
        'indicators': indicators,
        'performance_forms': performance_forms,
        'add_form': add_form,
        'user_role': request.user.role,
        'technical_fields': technical_fields,
        'organizational_fields': organizational_fields,
        'behavioral_fields': behavioral_fields,
    }
    return render(request, 'performance.html', context)


@login_required
def performance_indicator_create(request):
    if request.user.role != 'company_owner':
        messages.error(request, "Unauthorized access.")
        return redirect('performance_indicator_list')

    if request.method == 'POST':
        form = PerformanceIndicatorForm(request.POST, company=request.user.company)
        if form.is_valid():
            indicator = form.save(commit=False)
            indicator.company = request.user.company
            indicator.added_by = request.user
            indicator.save()
            messages.success(request, "Performance Indicator added.")
        else:
            messages.error(request, "Failed to add indicator.")
    return redirect('performance_indicator_list')


@login_required
def performance_indicator_update(request, pk):
    performance = get_object_or_404(PerformanceIndicator, pk=pk, company=request.user.company)

    if request.user.role != 'company_owner':
        messages.error(request, "Unauthorized access.")
        return redirect('performance_indicator_list')

    if request.method == 'POST':
        form = PerformanceIndicatorForm(request.POST, instance=performance, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, "Performance Indicator updated.")
    return redirect('performance_indicator_list')


@login_required
def performance_indicator_delete(request, pk):
    performance = get_object_or_404(PerformanceIndicator, pk=pk, company=request.user.company)

    if request.user.role != 'company_owner':
        messages.error(request, "Unauthorized access.")
        return redirect('performance_indicator_list')

    if request.method == 'POST':
        performance.delete()
        messages.success(request, "Performance Indicator deleted.")
    return redirect('performance_indicator_list')


@login_required
def performance_indicator_toggle_status(request, pk, new_status):
    performance = get_object_or_404(PerformanceIndicator, pk=pk, company=request.user.company)

    if request.user.role != 'company_owner':
        messages.error(request, "Unauthorized access.")
        return redirect('performance_indicator_list')

    if new_status.lower() in ['active', 'inactive']:
        performance.status = new_status.lower()
        performance.save()
    return redirect('performance_indicator_list')


# ======= APPRAISAL VIEWS =======

def get_appraisal_context(form=None, mode='list', instance=None, company=None):
    appraisals = PerformanceAppraisal.objects.filter(company=company).order_by('-date')
    appraisal_list = [{'instance': a, 'form': PerformanceAppraisalForm(instance=a, company=company)} for a in appraisals]

    context = {
        'appraisals': appraisal_list,
        'form': form or PerformanceAppraisalForm(company=company),
        'mode': mode,
        'title': f'{mode.capitalize()} Performance Appraisal',
        'tech_fields': TECH_FIELDS,
        'org_fields': ORG_FIELDS,
        'technical_indicators': TECH_COMPETENCIES,
        'organizational_indicators': ORG_COMPETENCIES,
    }
    if instance and mode == 'edit':
        context['edit_instance'] = instance
    return context


@login_required
def appraisal_list(request):
    form = PerformanceAppraisalForm(company=request.user.company)
    context = get_appraisal_context(form=form, mode='list', company=request.user.company)
    return render(request, 'performance_appraisal_list.html', context)


@login_required
def appraisal_create(request):
    if request.user.role != 'company_owner':
        messages.error(request, "Unauthorized access.")
        return redirect('appraisal_list')

    if request.method == 'POST':
        form = PerformanceAppraisalForm(request.POST, company=request.user.company)
        if form.is_valid():
            appraisal = form.save(commit=False)
            appraisal.company = request.user.company
            appraisal.appraiser = request.user
            appraisal.save()
            messages.success(request, 'Appraisal added successfully.')
            return redirect('appraisal_list')
        else:
            messages.error(request, 'Please correct the errors in the form.')
            return render(request, 'performance_appraisal_list.html',
                          get_appraisal_context(form=form, mode='add', company=request.user.company))


@login_required
def appraisal_update(request, pk):
    instance = get_object_or_404(PerformanceAppraisal, pk=pk, company=request.user.company)

    if request.user.role != 'company_owner':
        messages.error(request, "Unauthorized access.")
        return redirect('appraisal_list')

    if request.method == 'POST':
        form = PerformanceAppraisalForm(request.POST, instance=instance, company=request.user.company)
        if form.is_valid():
            appraisal = form.save(commit=False)
            appraisal.appraiser = request.user
            appraisal.save()
            messages.success(request, 'Appraisal updated successfully.')
            return redirect('appraisal_list')
        else:
            messages.error(request, 'Please correct the errors.')
    else:
        form = PerformanceAppraisalForm(instance=instance, company=request.user.company)

    return render(request, 'performance_appraisal_list.html',
                  get_appraisal_context(form=form, mode='edit', instance=instance, company=request.user.company))


@login_required
def appraisal_delete(request, pk):
    instance = get_object_or_404(PerformanceAppraisal, pk=pk, company=request.user.company)

    if request.user.role != 'company_owner':
        messages.error(request, "Unauthorized access.")
        return redirect('appraisal_list')

    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'Appraisal deleted successfully.')
    return redirect('appraisal_list')




def performance_list(request):
    return render(request, 'performance1.html')
