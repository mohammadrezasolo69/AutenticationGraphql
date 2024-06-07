from django.contrib.auth import get_user_model

import graphene
from graphene_django import DjangoObjectType


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
        opt_code = 123456
        # send_sms()
        return RequestOtp(ok=True, message='otp send .')


class Mutation(graphene.ObjectType):
    request_otp = RequestOtp.Field()

