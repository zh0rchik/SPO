from django.db import models


class MyObject(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    value = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    target = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=50)
    data_type = models.CharField(max_length=50)
    parent = models.CharField(max_length=255, null=True, blank=True)
    uploaded_file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return self.value
