from django.db import models
from django.contrib.auth.models import User
from accounts.models import Company
from superadmin.models import Package

# Create your models here.
class SubscribedCompany(models.Model):
        company = models.ForeignKey(Company, on_delete=models.CASCADE)
        package = models.ForeignKey(Package, on_delete=models.CASCADE)
        subscribed_on = models.DateTimeField(auto_now_add=True)
        


        def __str__(self):
            return f"{self.company.name} - {self.package.plan_name}"

        class Meta:
            unique_together = ('company', 'package')