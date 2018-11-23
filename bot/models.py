from django.db import models

# Create your models here.

class MessengerUser(models.Model):
    uid=models.TextField(max_length=25)
    first_name=models.TextField(max_length=30)
    last_name=models.TextField(max_length=30)
    email=models.EmailField(max_length=100,null=True)
    appid=models.TextField(max_length=25,null=True)