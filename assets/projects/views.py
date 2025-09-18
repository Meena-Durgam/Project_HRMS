from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
import json

from .models import Project, Task, TaskProgress
from .forms import ProjectForm, TaskForm, TaskProgressForm
from clients.models import Client
from employee.models import Employee
from django.db import models
from notifications.utils import notify_roles


@login_required
def my_projects_view(request):
    try:
        employee = request.user.employee_account  # Assuming OneToOneField from User to Employee
    except Employee.DoesNotExist:
        return render(request, 'projects/my_projects.html', {'error': 'Employee profile not found.'})

    # Fetch projects where the user is either team leader or in team members
    projects = Project.objects.filter(
        models.Q(team_leader=employee) | models.Q(team_members=employee)
    ).distinct()

    return render(request, 'my_projects.html', {'projects': projects})


@login_required
def project_list(request):
    company = request.user.company
    projects = Project.objects.filter(company=company) \
        .select_related('client', 'team_leader') \
        .prefetch_related('team_members')

    clients = Client.objects.filter(company=company)
    team_leaders = Employee.objects.filter(company=company)
    employees = Employee.objects.filter(company=company)

    # ✅ Filters
    project_query = request.GET.get('project', '')
    employee_query = request.GET.get('employee', '')
    status_query = request.GET.get('status', '')

    if project_query:
        projects = projects.filter(name__icontains=project_query)

    if employee_query:
        projects = projects.filter(
            Q(team_leader__first_name__icontains=employee_query) |
            Q(team_leader__last_name__icontains=employee_query) |
            Q(team_members__first_name__icontains=employee_query) |
            Q(team_members__last_name__icontains=employee_query)
        ).distinct()

    if status_query:
        projects = projects.filter(status__iexact=status_query)

    # ✅ Add Project
    if request.method == 'POST' and 'add_project' in request.POST:
        form = ProjectForm(request.POST, request.FILES, company=company)
        if form.is_valid():
            project = form.save(commit=False)
            project.company = company
            project.save()
            form.save_m2m()
            messages.success(request, "Project created successfully")

            # ✅ Notify employees about new project
            notify_roles(
                roles=['employee'],
                message=f"Project '{project.name}' was created by {request.user.username}.",
                url='/projects/',
                sender=request.user
            )
            return redirect('project_list')
        else:
            messages.error(request, "Please fill in all required fields.")
    else:
        form = ProjectForm(company=company)

    # ✅ Forms for editing each project
    edit_forms = {p.id: ProjectForm(instance=p, company=company) for p in projects}

    return render(request, 'project_dashboard.html', {
        'projects': projects,
        'clients': clients,
        'team_leaders': team_leaders,
        'employees': employees,
        'form': form,
        'edit_forms': edit_forms,
        'project_query': project_query,
        'employee_query': employee_query,
        'status_query': status_query,
    })

@login_required
def project_update(request, pk):
    company = request.user.company
    project = get_object_or_404(Project, pk=pk, company=company)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project, company=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully")

            # ✅ Notify employees about project update
            notify_roles(
                roles=['employee'],
                message=f"Project '{project.name}' was updated by {request.user.username}.",
                url='/projects/',
                sender=request.user
            )
            return redirect('project_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProjectForm(instance=project, company=company)
    return render(request, 'project_dashboard.html', {
        'form': form,
        'project': project,
    })

@login_required
def project_delete(request, pk):
    company = request.user.company
    project = get_object_or_404(Project, pk=pk, company=company)

    # ✅ Capture name before deletion
    project_name = project.name

    project.delete()
    messages.success(request, "Project deleted successfully")

    # ✅ Notify employees about deletion
    notify_roles(
        roles=['employee'],
        message=f"Project '{project_name}' was deleted by {request.user.username}.",
        url='/projects/',
        sender=request.user
    )
    return redirect('project_list')

@login_required
def project_view(request, pk):
    company = request.user.company
    project = get_object_or_404(Project, pk=pk, company=company)

    tasks = project.tasks.all()
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='completed').count()
    open_tasks = total_tasks - completed_tasks
    progress = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

    context = {
        'project': project,
        'tasks': tasks,
        'progress': progress,
        'completed_tasks': completed_tasks,
        'open_tasks': open_tasks,
    }
    return render(request, 'project_detail.html', context)

@login_required
def update_priority(request, project_id):
    project = get_object_or_404(Project, id=project_id, company=request.user.company)

    try:
        employee = request.user.employee_account
    except Employee.DoesNotExist:
        raise PermissionDenied("Employee profile not found.")

    # ✅ Allow only team leader
    if project.team_leader != employee:
        raise PermissionDenied("You are not authorized to update the priority of this project.")

    if request.method == 'POST':
        new_priority = request.POST.get('priority')
        if new_priority:
            project.priority = new_priority
            project.save()
            messages.success(request, "Project priority updated.")
        else:
            messages.error(request, "Priority value is missing.")

    return redirect('my_projects')


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from .models import Project, Employee

@login_required
def update_status(request, project_id):
    project = get_object_or_404(Project, id=project_id, company=request.user.company)

    try:
        employee = request.user.employee_account
    except Employee.DoesNotExist:
        return redirect('my_projects')  # Replace with your URL name

    if project.team_leader != employee:
        return redirect('my_projects')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            project.status = new_status
            project.save()
        return redirect('my_projects')  # Always redirect after POST

    return redirect('my_projects')

@login_required
def task_list(request):
    if request.user.role == 'company_owner':
        raise PermissionDenied("Company owners are not allowed to access this page.")

    company = request.user.company
    employee = getattr(request.user, 'employee_account', None)

    if not employee:
        raise PermissionDenied("You are not registered as an employee.")

    # ✅ Fetch ALL projects where the employee is team leader OR team member
    projects = Project.objects.filter(
        Q(team_leader=employee) |
        Q(team_members=employee),
        company=company
    ).distinct()

    # ✅ Fetch only tasks the employee can see
    visible_tasks = Task.objects.filter(
        Q(assigned_to=employee) |
        Q(project__team_leader=employee) |
        Q(project__team_members=employee),
        project__company=company
    ).distinct()

    # ✅ Count visible tasks per project (will be 0 if no tasks assigned yet)
    project_task_counts = {
        project.id: visible_tasks.filter(project=project).count()
        for project in projects
    }

    # ✅ Add total_tasks attribute to each project
    for project in projects:
        project.total_tasks = project_task_counts.get(project.id, 0)

    # ✅ Task form
    form = TaskForm(user=request.user)
    task_forms = {task.id: TaskForm(instance=task, user=request.user) for task in visible_tasks}

    return render(request, 'task_dashboard.html', {
        'tasks': visible_tasks,
        'projects': projects,
        'form': form,
        'task_forms': task_forms  # edit forms
    })


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Task, Project
from .forms import TaskForm

@login_required
def create_task(request):
    company = request.user.company
    employee = getattr(request.user, 'employee_account', None)

    if not employee:
        raise PermissionDenied("Only employees can create tasks.")

    project_id = request.GET.get('project_id') or request.POST.get('project')
    if not project_id:
        messages.error(request, "Project ID is required to create a task.")
        return redirect('task_list')

    project = get_object_or_404(Project, id=project_id, company=company)

    # ✅ Allow only team leader to create task
    if project.team_leader != employee:
        raise PermissionDenied("You are not authorized to create tasks for this project.")

    if request.method == 'POST':
        form = TaskForm(request.POST or None, request.FILES or None, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.save()
            form.save_m2m()
            messages.success(request, "Task created successfully!")

            # ✅ Notify the assigned employee
            if task.assigned_to:
                notify_roles(
                    roles=['employee'],
                    message=f"You were assigned a new task '{task.title}' in project '{project.name}' by {request.user.username}.",
                    url='/tasks/',
                    sender=request.user
                )
            return redirect('task_list')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = TaskForm(user=request.user, project=project)

    tasks = Task.objects.filter(project=project)
    return render(request, 'task_dashboard.html', {
        'form': form,
        'project': project,
        'tasks': tasks,
    })
@login_required
def get_project_team_members(request):
    project_id = request.GET.get('project_id')
    try:
        project = Project.objects.get(id=project_id)
        team_members = project.team_members.all()
        data = [{'id': member.id, 'name': f'{member.first_name} {member.last_name}'} for member in team_members]
        return JsonResponse({'members': data})
    except Project.DoesNotExist:
        return JsonResponse({'members': []})
@login_required
def edit_task(request, pk):
    company = request.user.company
    task = get_object_or_404(Task, pk=pk, project__company=company)

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')

            notify_roles(
                roles=['employee'],
                message=f"Task '{task.title}' was updated in project '{task.project.name}' by {request.user.username}.",
                url='/tasks/',
                sender=request.user
            )
            return redirect('task_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(instance=task, company=company)

    tasks = Task.objects.filter(project__company=company)
    projects = Project.objects.filter(company=company)
    employees = Employee.objects.filter(company=company)

    return render(request, 'task_dashboard.html', {
        'tasks': tasks,
        'projects': projects,
        'employees': employees,
        'edit_form': form,
    })

@login_required
def task_view(request, task_id):
    company = request.user.company
    task = get_object_or_404(Task, pk=task_id, project__company=company)
    return render(request, 'task_view.html', {'task': task})
@login_required
def update_task_priority(request, task_id):
    company = request.user.company
    employee = getattr(request.user, 'employee_account', None)
    task = get_object_or_404(Task, pk=task_id, project__company=company)

    if employee != task.project.team_leader:
        raise PermissionDenied("Only the team leader can update task priority.")

    if request.method == 'POST':
        priority = request.POST.get('priority')
        if priority in dict(Task.PRIORITY_CHOICES):
            task.priority = priority
            task.save()
            messages.success(request, f'Priority updated to {priority.capitalize()}.')
    return redirect('task_list')


@login_required
def update_task_status(request, task_id):
    company = request.user.company
    employee = getattr(request.user, 'employee_account', None)
    task = get_object_or_404(Task, pk=task_id, project__company=company)

    if employee not in task.project.team_members.all():
        raise PermissionDenied("Only team members can update task status.")

    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(Task.STATUS_CHOICES):
            task.status = status
            task.save()
            messages.success(request, f'Status updated to {status.capitalize()}.')
    return redirect('task_list')


@login_required
def add_task_progress(request, task_id):
    company = request.user.company
    task = get_object_or_404(Task, id=task_id, project__company=company)
    employee = getattr(request.user, 'employee_account', None)

    if not employee:
        raise PermissionDenied("You are not registered as an employee.")
    if task.assigned_to != employee:
        raise PermissionDenied("You are not authorized to update this task.")

    progress_updates = TaskProgress.objects.filter(task=task).order_by('-date')

    if request.method == "POST":
        form = TaskProgressForm(request.POST, request.FILES)
        if form.is_valid():
            progress = form.save(commit=False)
            progress.task = task
            progress.employee = employee
            progress.save()
            messages.success(request, "Progress updated successfully!")

            # ✅ Notify team leader
            if task.project.team_leader:
                notify_roles(
                    roles=['employee'],
                    message=f"{employee.first_name} updated progress on task '{task.title}' in project '{task.project.name}'.",
                    url='/tasks/',
                    sender=request.user
                )
            return redirect('task_list')
    else:
        form = TaskProgressForm()

    return render(request, 'taskprogress.html', {
        'form': form,
        'task': task,
        'progress_updates': progress_updates,
    })

@login_required
def task_delete(request, task_id):
    company = request.user.company
    task = get_object_or_404(Task, pk=task_id, project__company=company)

    # ✅ Save task title before deleting
    task_title = task.title
    project_name = task.project.name
    task.delete()
    messages.success(request, 'Task deleted successfully.')

    # ✅ Notify team members or employees
    notify_roles(
        roles=['employee'],
        message=f"Task '{task_title}' was deleted from project '{project_name}' by {request.user.username}.",
        url='/tasks/',
        sender=request.user
    )

    return redirect('task_list')


from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Task, TaskProgress

@login_required
def task_board(request):
    company = request.user.company
    
    # Prefetch only the latest progress per task
    tasks = Task.objects.filter(project__company=company).prefetch_related(
        Prefetch(
            'progress_updates',
            queryset=TaskProgress.objects.order_by('-date', '-id'),
            to_attr='latest_progress'
        )
    )

    # Grouping structure
    task_groups = {
        'To_Do': [],
        'In_Progress': [],
        'Review': [],
        'Completed': [],
    }

    for task in tasks:
        latest_progress = task.latest_progress[0] if task.latest_progress else None
        status = task.status  # We'll use this in the template for color mapping

        if status in task_groups:
            task_groups[status].append({
                'task': task,
                'status': status,
                'latest_progress': latest_progress
            })

    context = {
        'task_groups': task_groups
    }
    return render(request, 'task_board.html', context)


@csrf_exempt
@login_required
def update_task_status_ajax(request, task_id):
    if request.method == 'POST':
        try:
            company = request.user.company
            task = Task.objects.get(id=task_id, project__company=company)
            data = json.loads(request.body)
            new_status = data.get('status')
            task.status = new_status
            task.save()
            return JsonResponse({'message': 'Status updated'}, status=200)
        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@login_required
def get_team_members(request, project_id):
    company = request.user.company
    try:
        project = Project.objects.get(id=project_id, company=company)
        team_members = list(project.team_members.values('employee_id', 'first_name', 'last_name'))
        return JsonResponse({'members': team_members})
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'},status=404)