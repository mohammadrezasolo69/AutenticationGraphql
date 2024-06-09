from django.contrib.auth import get_user_model


def jwt_payload_handler(user, *args, **kwargs):
    payload = {
        'user_id': user.id,
        'phone_number': str(user.phone_number),
    }
    return payload
