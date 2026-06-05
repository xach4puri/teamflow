"""
Custom form validators for TeamFlow — Session 05

Validators are functions that raise a ValidationError if the value
doesn't meet the required conditions. They can be used in forms or models.
"""
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_future_deadline(value):
    """
    Validates that a deadline date is not in the past.

    This validator is used in TaskForm to prevent users from setting
    deadlines on dates that have already passed.
    """
    if value and value < timezone.now().date():
        raise ValidationError(
            'Deadline cannot be in the past. Please choose today or a future date.',
            code='deadline_in_past',
        )
