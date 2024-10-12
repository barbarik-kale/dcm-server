import uuid
from django.db import models

class User(models.Model):
    # A user account

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=False, unique=True, editable=False)
    password = models.CharField(blank=False, max_length=100)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email
        }

class Drone(models.Model):
    """
    Drone is an unmanned aerial vehicle
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(null=True, blank=True, max_length=20)
    avg_speed_ms = models.FloatField(null=True)
    flight_time_seconds = models.IntegerField(null=False)
    last_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    last_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avg_speed_ms': self.avg_speed_ms,
            'flight_time_seconds': self.flight_time_seconds,
            'last_latitude': self.last_latitude,
            'last_longitude': self.last_longitude
        }