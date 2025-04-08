import base64

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.contrib.auth import authenticate
from django.core.files.base import ContentFile


from api.validators import MaxLengthValidator, is_not_number
from api.exceptions import UserNotFoundError, WrongPassword, InvalidData
from reciepts.models import (
    CustomUser,
    Tag,
    Ingredient,
    Reciept,
    IngredientReciept,
)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]

            data = ContentFile(base64.b64decode(imgstr), name="img." + ext)

        return super().to_internal_value(data)


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    username_field = CustomUser.EMAIL_FIELD

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            raise UserNotFoundError()
        if not user.check_password(password):
            raise WrongPassword()
        access_token = AccessToken.for_user(user)
        return {"auth_token": str(access_token)}


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UniqueValidator(queryset=CustomUser.objects.all()),
            RegexValidator(
                regex=r"^[\w.@+-]+\Z",
                message="Недопустимые символы в username.",
            ),
        ],
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())],
    )
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = CustomUser
        fields = ("avatar",)


class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
        validators=[validate_password],
    )
    current_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        user = self.context.get("user")
        current_password = attrs.get("current_password")
        if not user.check_password(current_password):
            raise WrongPassword()
        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data.pop("new_password")
        instance.set_password(new_password)
        instance.save()
        return instance

    class Meta:
        model = CustomUser
        fields = ("new_password", "current_password")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientInRecieptSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )
    amount = serializers.IntegerField(min_value=1)


class IngredientInRecieptReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientReciept
        fields = ["id", "name", "measurement_unit", "amount"]


class TestSerializer(serializers.ModelSerializer):
    amount = serializers.ReadOnlyField(source="i2r.amount")

    class Meta:
        model = Ingredient
        fields = ["id", "name", "measurement_unit", "amount"]


class RecieptCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecieptSerializer(many=True)
    image = Base64ImageField(required=True)
    author = UserSerializer(required=False)

    class Meta:
        model = Reciept
        fields = [
            "id",
            "name",
            "image",
            "cooking_time",
            "text",
            "author",
            "tags",
            "ingredients",
        ]

    def create(self, validated_data: dict):
        user = self.context.get("request").user
        ingredients_data = validated_data.pop("ingredients")
        tags_data = validated_data.pop("tags")
        reciept = Reciept.objects.create(**validated_data, author=user)
        reciept.tags.set(tags_data)
        self._save_ingredients(ingredients_data, reciept)
        return reciept

    def _save_ingredients(
        self, ingredients_data: list[dict], reciept: Reciept
    ):
        for item in ingredients_data:
            ingredient = Ingredient.objects.get(id=item["id"])
            obj = IngredientReciept.objects.create(
                reciept=reciept, ingredient=ingredient, amount=item["amount"]
            )


class RecieptSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserSerializer(read_only=True)
    # ingredients = IngredientInRecieptReadSerializer(many=True)
    ingredients = TestSerializer(many=True)
    image = Base64ImageField(required=True)
    name = serializers.CharField(required=True)
    text = serializers.CharField(required=True)
    cooking_time = serializers.IntegerField(required=True)

    class Meta:
        model = Reciept
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
