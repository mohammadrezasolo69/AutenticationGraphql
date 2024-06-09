from django.contrib.auth import get_user_model

import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required
from graphene_django import DjangoObjectType
from graphql_jwt.shortcuts import create_refresh_token, get_token

from accounts.selectors import get_user_by_phone_number
from accounts.services import get_or_create_user
from utils.redis_connection import redis_set, redis_get, redis_delete
from utils.generate_random_code import generate_random
from utils.sender import sms_sender


# ------------------------------------- Query -------------------------------------------------
class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = (
            'id', 'phone_number', 'is_active', 'first_name', 'last_name',
            'is_superuser', 'is_staff', 'is_verify', 'verify_date',
        )


class Query(graphene.ObjectType):
    user = graphene.Field(UserType, phone_number=graphene.String())

    @staticmethod
    @login_required
    def resolve_user(root, info, phone_number=None):
        user = get_user_by_phone_number(phone_number=phone_number)
        return user


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
    access_token = graphene.String(default_value=None)
    refresh_token = graphene.String(default_value=None)

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

        # create jwt token
        access_token = get_token(user)
        refresh_token = create_refresh_token(user)

        # delete otp code from cache
        redis_delete(key=phone_number)

        return VerifyOtp(
            ok=True, is_new_user=is_new_user, message='successfully',
            user=user, access_token=access_token, refresh_token=refresh_token
        )


class ChangePassword(graphene.Mutation):
    class Arguments:
        new_password = graphene.String()
        repeat_new_password = graphene.String()

    ok = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType, default_value=None)

    @staticmethod
    @login_required
    def mutate(root, info, new_password: str, repeat_new_password: str):
        if new_password != repeat_new_password:
            return ChangePassword(ok=False, message=f'new_password and repeat_new_password not match .')

        user = info.context.user
        user.set_password(new_password)
        user.save(update_fields=['password'])

        return ChangePassword(ok=True, message=f'password is change', user=user)


class Mutation(graphene.ObjectType):
    request_otp = RequestOtp.Field()
    verify_otp = VerifyOtp.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    change_password = ChangePassword.Field()
