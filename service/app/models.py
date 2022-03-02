from django.db import models

# from django.utils import timezone


class Vehicle(models.Model):
    user_id = models.IntegerField()
    allowed_actions = models.JSONField()
    allowed_properties = models.JSONField()

    model = models.CharField(max_length=50)
    body = models.CharField(max_length=50)
    color = models.CharField(max_length=7)
    plate_number = models.CharField(max_length=20)
    date = models.DateField()

    vin = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.vin}"
