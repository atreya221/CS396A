from email.policy import default
from django.db import models

# Create your models here.

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    username = models.CharField(max_length=20, unique=True, blank=False)
    email = models.EmailField(max_length=100, unique=True, blank=False)
    password = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return str(self.user_id)

class FileForm(models.Model):
    file_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.CharField(max_length=100, blank=False)
    file = models.FileField()

    def publish(self):
        self.save()

    def __str__(self):
        return str(self.file_id)
