from django.db import models
from django.conf import settings
from clients.models import Client
from accounts.models import Company
from employee.models import Employee


class Ticket(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='tickets'
    )

    ticket_id = models.CharField(
        max_length=20, unique=True, blank=True, editable=False
    )
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    assigned_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client_tickets'
    )

    cc = models.EmailField(blank=True, null=True)

    priority = models.CharField(
        max_length=10,
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High')
        ],
        default='Medium'
    )

    status = models.CharField(
        max_length=10,
        choices=[
            ('New', 'New'),
            ('Open', 'Open'),
            ('Reopened', 'Reopened'),
            ('Solved', 'Solved'),
            ('Pending', 'Pending')
        ],
        default='New'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    last_reply = models.DateTimeField(null=True, blank=True)

    followers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='ticket_followers'
    )

    file = models.FileField(upload_to='tickets/files/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            last_ticket = Ticket.objects.filter(company=self.company).order_by('id').last()
            next_id = 1 if not last_ticket else last_ticket.id + 1
            self.ticket_id = f"TKT-{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_id} - {self.subject}"

    def get_assigned_employee(self):
        return getattr(self.assigned_staff, 'employee_account', None)

    def get_following_employees(self):
        return [getattr(user, 'employee_account', None) for user in self.followers.all()]


class TicketComment(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='ticket_comments'
    )

    ticket = models.ForeignKey(
        Ticket,
        related_name='comments',
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.ticket.ticket_id}"

    def get_employee(self):
        return getattr(self.user, 'employee_account', None)
