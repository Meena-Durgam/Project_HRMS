from django.db import models
from clients.models import Client
from employee.models import Employee
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
from accounts.models import Company
from department.models import Department
  # adjust import if needed


from ckeditor.fields import RichTextField  # ✅ Import CKEditor field

class Project(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='projects', verbose_name='Company')
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE,null=True, blank=True, related_name='projects'
    )
    STATUS_CHOICES = [
        ('Planned', 'Planned'),
        ('In Progress', 'In Progress'),
        ('Onboard', 'Onboard'),
        ('Completed', 'Completed'),
        ('Cancel', 'Cancel'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planned')
    name = models.CharField(max_length=255, verbose_name='Project Name')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client')
    start_date = models.DateField(verbose_name='Start Date')
    end_date = models.DateField(verbose_name='End Date')
    
    priority = models.CharField(
        max_length=10,
        choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
        verbose_name='Priority'
    )

    status_choices = [
        ('Not Started', 'Not Started'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
    ]

    team_leader = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leading_projects', verbose_name='Team Leader')
    team_members = models.ManyToManyField(Employee, related_name='project_memberships', verbose_name='Team Members')
    
    description = RichTextField(verbose_name='Description')  # ✅ Replaced TextField with RichTextField
    
    status = models.CharField(max_length=20, choices=status_choices, default='Not Started', verbose_name='Status')
    file_upload = models.FileField(upload_to='projects/', null=True, blank=True, verbose_name='Project File')

    def save(self, *args, **kwargs):
        if self.start_date and self.end_date and self.end_date >= self.start_date:
            days = (self.end_date - self.start_date).days + 1
            self.total_work_hours = days * 8
        else:
            self.total_work_hours = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

class Task(models.Model):
    STATUS_CHOICES = [
        ('To_Do', 'To Do'),
        ('In_Progress', 'In Progress'),
        ('Review', 'Review'),
        ('Completed', 'Completed'),
    ]

    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    task_id = models.CharField(max_length=20, unique=True, editable=False, verbose_name='Task ID',null=True,blank=True)
    title = models.CharField(max_length=255, verbose_name='Task Title')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks', verbose_name='Project')
    assigned_to = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Assigned To')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To_Do', verbose_name='Status')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='Priority')
    start_date = models.DateField(null=True, blank=True, verbose_name='Start Date')
    due_date = models.DateField(null=True, blank=True, verbose_name='Due Date')
    description = models.TextField(blank=True, verbose_name='Description')
    attachment = models.FileField(upload_to='tasks/', null=True, blank=True, verbose_name='Attachment')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='Created At')

    def __str__(self):
        return self.title

    def clean(self):
        if self.assigned_to and self.project:
            if self.assigned_to not in self.project.team_members.all():
                raise ValidationError(f"{self.assigned_to} is not a member of the project's team.")

    def save(self, *args, **kwargs):
        if not self.task_id:
            last_task = Task.objects.all().order_by('id').last()
            if last_task and last_task.task_id:
                last_id_num = int(last_task.task_id.replace('ID-', ''))
                self.task_id = f'ID-{last_id_num + 1:02d}'
            else:
                self.task_id = 'ID-01'
        super().save(*args, **kwargs)



class TaskProgress(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='progress_updates', verbose_name='Task')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Employee')
    date = models.DateField(auto_now_add=True, verbose_name='Date')
    progress_description = models.TextField(verbose_name='Progress Description')
    percentage_complete = models.PositiveIntegerField(default=0, verbose_name='Percentage Complete')
    attachment = models.FileField(upload_to='task_progress/', null=True, blank=True, verbose_name='Attachment')

    def __str__(self):
        return f"{self.employee} - {self.task.title} ({self.percentage_complete}%)"
