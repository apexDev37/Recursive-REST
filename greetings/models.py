import uuid

from django.core.exceptions import ValidationError
from django.db import models

from greetings.utils.validators import (
  GreetingParamValidator,
  GreetingValueValidator,
) 

"""
  Module Name:      greetings/models.py
  Module Purpose:   contains the Django models for the greetings application.
  Author:           apexDev37 (Eugene M.)
  Version:          1.0
  Last Modified:    01/07
  Dependencies:     uuid, models
"""


class Greeting(models.Model):
    """
    Represents a custom greeting from a user.
    """

    greeting_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    greeting_text = models.CharField(
      unique=True, 
      blank=False, 
      max_length=50,
      validators=[GreetingParamValidator(), GreetingValueValidator()])
    greeting_created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        ordering = ["greeting_created_at"]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
