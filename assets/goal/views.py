from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Goal, GoalType
from .forms import GoalForm, GoalTypeForm
from notifications.utils import notify_roles  # ✅ Notification import

# 🔸 GOAL TYPE CRUD (Company Owner Only)
@login_required
def goal_type_list(request):
    user = request.user
    role = user.role
    company = user.company
    types = GoalType.objects.filter(company=company)

    if request.method == 'POST':
        if role != 'company_owner':
            messages.error(request, "You are not authorized to modify Goal Types.")
            return redirect('goal_type_list')

        if 'add_type' in request.POST:
            form = GoalTypeForm(request.POST)
            if form.is_valid():
                goal_type = form.save(commit=False)
                goal_type.company = company
                goal_type.save()
                messages.success(request, 'Goal Type added successfully.')

                # ✅ Notify employees
                notify_roles(
                    roles=['employee'],
                    message=f"A new Goal Type '{goal_type.name}' was added by {request.user.username}.",
                    url='/goal-types/',
                    sender=user
                )

                return redirect('goal_type_list')

        elif 'edit_type' in request.POST:
            goal_id = request.POST.get('goal_id')
            goal_type = get_object_or_404(GoalType, id=goal_id, company=company)
            form = GoalTypeForm(request.POST, instance=goal_type)
            if form.is_valid():
                form.save()
                messages.success(request, 'Goal Type updated successfully.')

                # ✅ Notify employees
                notify_roles(
                    roles=['employee'],
                    message=f"Goal Type '{goal_type.name}' was updated by {request.user.username}.",
                    url='/goal-types/',
                    sender=user
                )

                return redirect('goal_type_list')

        elif 'delete_type' in request.POST:
            goal_id = request.POST.get('goal_id')
            goal_type = get_object_or_404(GoalType, id=goal_id, company=company)
            goal_name = goal_type.name
            goal_type.delete()
            messages.success(request, 'Goal Type deleted successfully.')

            # ✅ Notify employees
            notify_roles(
                roles=['employee'],
                message=f"Goal Type '{goal_name}' was deleted by {request.user.username}.",
                url='/goal-types/',
                sender=user
            )

            return redirect('goal_type_list')

    return render(request, 'goal_type.html', {
        'types': types,
        'role': role
    })


# 🔸 GOAL LISTING (All Employees + Company Owner)
@login_required
def goal_list(request):
    user = request.user
    company = user.company

    if user.role == 'company_owner':
        goals = Goal.objects.filter(company=company)
    else:
        goals = Goal.objects.filter(company=company, created_by=user)

    add_form = GoalForm(company=company)

    edit_forms = {
        goal.id: GoalForm(instance=goal, company=company)
        for goal in goals
    }

    return render(request, 'goal_tracking.html', {
        'goals': goals,
        'add_form': add_form,
        'edit_forms': edit_forms,
        'role': user.role
    })


# 🔸 GOAL CREATION
@login_required
def add_goal(request):
    user = request.user
    company = user.company

    if request.method == 'POST':
        form = GoalForm(request.POST, company=company)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.created_by = user
            goal.company = company
            goal.save()
            messages.success(request, 'Goal added successfully.')

            # ✅ Notify employees
            notify_roles(
                roles=['employee'],
                message=f"{request.user.username} created a new goal: '{goal.title}'.",
                url='/goals/',
                sender=user
            )

            return redirect('goal_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = GoalForm(company=company)

    return render(request, 'goal_tracking.html', {
        'form': form,
        'action': 'Add',
        'role': user.role
    })


# 🔸 GOAL UPDATE
@login_required
def edit_goal(request, goal_id):
    user = request.user
    goal = get_object_or_404(Goal, id=goal_id, company=user.company)

    if user != goal.created_by and user.role != 'company_owner':
        messages.error(request, "You are not authorized to edit this goal.")
        return redirect('goal_list')

    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal, company=goal.company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Goal updated successfully.')

            # ✅ Notify employees
            notify_roles(
                roles=['employee'],
                message=f"{request.user.username} updated the goal: '{goal.title}'.",
                url='/goals/',
                sender=user
            )

            return redirect('goal_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = GoalForm(instance=goal, company=goal.company)

    return render(request, 'goal_tracking.html', {
        'form': form,
        'action': 'Edit',
        'role': user.role
    })


# 🔸 GOAL DELETE
@login_required
def delete_goal(request, goal_id):
    user = request.user
    goal = get_object_or_404(Goal, id=goal_id, company=user.company)

    if user != goal.created_by and user.role != 'company_owner':
        messages.error(request, "You are not authorized to delete this goal.")
        return redirect('goal_list')

    goal_title = goal.title
    goal.delete()
    messages.success(request, 'Goal deleted successfully.')

    # ✅ Notify employees
    notify_roles(
        roles=['employee'],
        message=f"{request.user.username} deleted the goal: '{goal_title}'.",
        url='/goals/',
        sender=user
    )

    return redirect('goal_list')
