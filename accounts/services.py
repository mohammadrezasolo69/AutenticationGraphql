from datetime import datetime

from django.contrib.auth import get_user_model
from accounts.selectors import get_user_by_phone_number


def get_or_create_user(phone_number):
    user = get_user_by_phone_number(phone_number=phone_number)
    if user is not None:
        return user, False
    user = get_user_model().objects.create(
        phone_number=phone_number, is_verify=True, verify_date=datetime.now(), is_active=True)
    return user, True
