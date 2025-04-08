from django.contrib import admin
from reciepts.models import Tag, Ingredient, Reciept, CustomUser


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("email", "username")


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


@admin.register(Reciept)
class RecieptAdmin(admin.ModelAdmin):
    list_display = ("name", "author_first_name")
    readonly_fields = ("favorited_count",)
    list_filter = ("tags",)
    search_fields = ("author", "name")

    def author_first_name(self, obj):
        return obj.author.first_name

    author_first_name.short_description = "Имя автора"


admin.site.register(Tag)
