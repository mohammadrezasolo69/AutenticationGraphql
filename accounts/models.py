from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from accounts.manager import CustomUserManager


class CustomUser(AbstractUser):
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('-id',)

    username = None

    phone_number_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="phone number not formatted correctly")
    phone_number = models.CharField(
        max_length=12, unique=True, verbose_name='Phone Number', db_index=True, validators=[phone_number_validator])
    is_verify = models.BooleanField(default=False, verbose_name='Verify')
    verify_date = models.DateTimeField(verbose_name='Verify Date',null=True, blank=True)
    create_date = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'phone_number'

    def __str__(self):
        return self.phone_number

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
