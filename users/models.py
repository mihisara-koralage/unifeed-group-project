from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        PAGE    = 'page',    'Page / Organisation'
        ADMIN   = 'admin',   'Admin'

    username = None
    email    = models.EmailField(unique=True)

    role        = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    bio         = models.TextField(blank=True)
    avatar      = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_page(self):
        return self.role == self.Role.PAGE

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN