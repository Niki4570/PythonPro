from django.db import models
from django.contrib.auth.models import User
from post_machine.models import PostMachine

# Create your models here.
class Parcel(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    sender = models.CharField(max_length=100)
    size = models.IntegerField()
    post_machine_recipient = models.ForeignKey(PostMachine, on_delete=models.CASCADE)
    order_datetime = models.DateTimeField("Date")
    open_datetime = models.DateTimeField("Date")
    status = models.BooleanField(default=False)
