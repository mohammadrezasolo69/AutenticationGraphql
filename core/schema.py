import graphene
import accounts.schema


class Query(graphene.ObjectType):
    name = graphene.String()


class Mutation(
    accounts.schema.Mutation,
    graphene.ObjectType
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)
