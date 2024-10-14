import uuid

from django.db import models

class User(models.Model):
    """
    A user account
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(blank=False, unique=True, editable=False)
    password = models.CharField(blank=False, max_length=100)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email
        }

