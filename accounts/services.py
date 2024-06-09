from typing import Dict, Tuple
from datetime import datetime

from django.contrib.auth import get_user_model
from accounts.selectors import get_user_by_phone_number


def get_or_create_user(phone_number:str) -> Tuple[get_user_model(), bool]:
    user = get_user_by_phone_number(phone_number=phone_number)
    if user is not None:
        return user, False
    user = get_user_model().objects.create(
        phone_number=phone_number, is_verify=True, verify_date=datetime.now(), is_active=True)
    return user, True


def update_profile_user(user: get_user_model(), items: Dict) -> get_user_model():
    for field, value in items.items():
        setattr(user, field, value)

        if field == 'phone_number':
            setattr(user, 'is_verify', False)
            setattr(user, "verify_date", None)

    user.save(update_fields=[str(key) for key in items.keys()])
    return user
