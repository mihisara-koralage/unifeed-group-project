"""Validation shared by student submissions, admin forms and link previews."""

import re
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_resource_url(value):
    if not re.fullmatch(r'https?://[^\s]+', value, flags=re.IGNORECASE) or any(
        ord(character) < 32 or ord(character) == 127 for character in value
    ):
        raise ValidationError('Please enter a valid URL starting with http:// or https://')
    URLValidator(schemes=['http', 'https'])(value)
    parts = urlsplit(value)
    if parts.username is not None or parts.password is not None:
        raise ValidationError('Resource links must not contain a username or password.')
