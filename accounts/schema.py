from django.contrib.auth import get_user_model

import graphene
from graphene_django import DjangoObjectType

from accounts.services import get_or_create_user
from utils.redis_connection import redis_set, redis_get, redis_delete
from utils.generate_random_code import generate_random
from utils.sender import sms_sender


# ------------------------------------- Query -------------------------------------------------
class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ('id', 'phone_number', 'is_active')


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
        # otp_code = generate_random(length=6, use_digit=True)
        otp_code = str(123456)
        redis_set(key=phone_number, data=otp_code, ex=120)
        sms_sender(phone_number=phone_number, body=otp_code)
        return RequestOtp(ok=True, message='otp send .')


class VerifyOtp(graphene.Mutation):
    class Arguments:
        phone_number = graphene.String(required=True)
        code = graphene.String(required=True)

    ok = graphene.Boolean()
    message = graphene.String()
    is_new_user = graphene.String(default_value=None)
    user = graphene.Field(UserType, default_value=None)

    @staticmethod
    def mutate(root, info, phone_number, code):
        # get otp_code from cache
        otp_code_cache = redis_get(key=phone_number)

        # check otp_code_cache no expiration
        if otp_code_cache is None:
            return VerifyOtp(ok=False, message='Code expiration')

        # check code is otp_code_cache
        if str(otp_code_cache) != code:
            return VerifyOtp(ok=False, message='Code incorrect')

        # create or get user
        user, is_new_user = get_or_create_user(phone_number=phone_number)

        # delete otp code from cache
        redis_delete(key=phone_number)

        return VerifyOtp(ok=True, is_new_user=is_new_user, message='successfully', user=user)


class Mutation(graphene.ObjectType):
    request_otp = RequestOtp.Field()
    verify_otp = VerifyOtp.Field()
