from django.db import models
from django.db.models import ForeignKey



class PostMachine(models.Model):
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city} located at {self.address}"

class Locker(models.Model):
    post_machine = ForeignKey(PostMachine, on_delete=models.CASCADE)
    size = models.IntegerField()
    status = models.BooleanField(default=False)


    def __str__(self):
        return f"Post machine:{self.post_machine.id}, size:{self.size}, status:{self.status}"
