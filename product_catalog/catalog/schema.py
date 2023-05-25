import graphene
from graphene_django import DjangoObjectType
import decimal
from .models import Category, Product


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "description", "products")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "category", 'price', 'quantity')


class UpdateCategory(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        name = graphene.String(required=True)
        id = graphene.ID()

    # The class attributes define the response of the mutation
    category = graphene.Field(CategoryType)

    @classmethod
    def mutate(cls, root, info, name, id):
        category = Category.objects.get(pk=id)
        category.name = name
        category.save()
        # Notice we return an instance of this mutation
        return UpdateCategory(category=category)


class CreateCategory(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        name = graphene.String(required=True)

    # The class attributes define the response of the mutation
    category = graphene.Field(CategoryType)

    @classmethod
    def mutate(cls, root, info, name):
        category = Category()
        category.name = name
        category.save()
        # Notice we return an instance of this mutation
        return CreateCategory(category=category)


class ProductInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()
    price = graphene.Float()
    quantity = graphene.Int()
    category = graphene.Int()


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, input):
        product = Product()
        product.name = input.name
        product.description = input.description
        product.price = decimal.Decimal(input.price)
        product.quantity = input.quantity
        product.category_id = input.category
        product.save()
        return CreateProduct(product=product)


class UpdateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)
        id = graphene.ID()

    product = graphene.Field(ProductType)

    @classmethod
    def mutate(cls, root, info, input, id):
        product = Product.objects.get(pk=id)
        product.name = input.name
        product.description = input.description
        product.price = decimal.Decimal(input.price)
        product.quantity = input.quantity
        product.category_id = input.category
        product.save()
        return UpdateProduct(product=product)


class Mutation(graphene.ObjectType):
    update_category = UpdateCategory.Field()
    create_category = CreateCategory.Field()
    create_product = CreateProduct.Field()
    update_product = UpdateProduct.Field()


class Query(graphene.ObjectType):
    products = graphene.List(
        ProductType,  category=graphene.String(required=False))
    categories = graphene.List(CategoryType)

    def resolve_products(root, info, category=None):
        if category:
            return Product.objects.filter(category__name=category)
        # We can easily optimize query count in the resolve method
        return Product.objects.select_related("category").all()

    def resolve_categories(root, info):
        return Category.objects.all()


schema = graphene.Schema(query=Query, mutation=Mutation)
