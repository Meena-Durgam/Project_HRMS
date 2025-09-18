from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    category = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default='#3788d8')

    def _str_(self):
        return self.title