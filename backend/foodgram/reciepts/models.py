from django.contrib.auth.models import AbstractUser
from django.db import models


from reciepts.constants import (
    MAX_USERNAME_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_NAME_LENGTH,
    MAX_SURNAME_LENGTH,
    MAX_RECIEPT_NAME_LENGTH,
    MAX_TAG_NAME_LENGTH,
    MAX_SLUG_NAME_LENGTH,
    MAX_INGREDIENT_NAME_LENGTH,
    MAX_MEASUREMENT_UNIT_LENGTH,
)


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_TAG_NAME_LENGTH, blank=False, verbose_name="Название"
    )
    slug = models.SlugField(
        max_length=MAX_SLUG_NAME_LENGTH, blank=False, verbose_name="Слаг"
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_INGREDIENT_NAME_LENGTH,
        blank=False,
        verbose_name="Название",
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT_LENGTH,
        blank=False,
        verbose_name="Единица измерения",
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Reciept(models.Model):
    name = models.CharField(
        max_length=MAX_RECIEPT_NAME_LENGTH, verbose_name="Название"
    )
    image = models.ImageField(
        upload_to="images/reciept_images/",
        blank=False,
        verbose_name="Картинка",
    )
    cooking_time = models.IntegerField(
        blank=False, verbose_name="Время приготовления"
    )
    text = models.TextField(blank=False, verbose_name="Описание")
    author = models.ForeignKey(
        "CustomUser",
        blank=False,
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )
    tags = models.ManyToManyField(Tag, blank=False, verbose_name="Теги")
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=False,
        through="IngredientReciept",
        verbose_name="Ингредиенты",
    )
    is_favorited = models.BooleanField(
        default=False, verbose_name="В избранном"
    )
    is_in_shopping_cart = models.BooleanField(
        default=False, verbose_name="В списке покупок"
    )
    favorited_count = models.IntegerField(
        default=0, verbose_name="Количество добавлений в избранное"
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientReciept(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    reciept = models.ForeignKey(Reciept, on_delete=models.CASCADE)
    amount = models.IntegerField()


class CustomUser(AbstractUser):
    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        verbose_name="Электронная почта",
    )
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        verbose_name="Имя пользователя",
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH, verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=MAX_SURNAME_LENGTH, verbose_name="Фамилия"
    )
    is_subscribed = models.BooleanField(default=False, verbose_name="Подписан")
    avatar = models.ImageField(
        upload_to="images/user_avatars/",
        null=True,
        default=None,
        verbose_name="Фото профиля",
    )
    subscriptions = models.ManyToManyField(
        "self", blank=True, verbose_name="Подписки"
    )
    shopping_cart = models.ManyToManyField(
        Ingredient, blank=True, verbose_name="Список покупок"
    )
    favorites = models.ManyToManyField(
        Reciept, blank=True, verbose_name="Избранное"
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
