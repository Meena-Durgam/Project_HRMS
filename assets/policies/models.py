from django.db import models
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField

User = get_user_model()

class Policy(models.Model):
    company = models.ForeignKey('accounts.Company', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = RichTextField(verbose_name='Description')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
