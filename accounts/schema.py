from django.contrib.auth import get_user_model

import graphene
from graphene_django import DjangoObjectType

from utils.redis_connection import redis_set, redis_get
from utils.generate_random_code import generate_random
from utils.sender import sms_sender


# ------------------------------------- Query -------------------------------------------------
class Query(graphene.ObjectType):
    pass


# ------------------------------------- Mutation -------------------------------------------------
class RequestOtp(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    @staticmethod
    def mutate(root, info, phone_number):
        opt_code = generate_random(length=6, use_digit=True)
        redis_set(key=phone_number, data=str(opt_code), ex=120)
        sms_sender(phone_number=phone_number, body=opt_code)
        return RequestOtp(ok=True, message='otp send .')


class Mutation(graphene.ObjectType):
    request_otp = RequestOtp.Field()
