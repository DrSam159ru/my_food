from urllib.parse import urljoin

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import CheckConstraint, Q, UniqueConstraint
from django.db.models.functions import Lower

from core.const import FIELD_LENGHT, MAX_FIELD_LENGHT, MID_FIELD_LENGHT


def recipe_image_upload_to(instance, filename):
    """
    Возвращает путь загрузки фото рецепта, основанный на ID автора.
    """
    author_id = getattr(instance.author, 'id', 'anon')
    return f'recipes/{author_id}/{filename}'


class Tag(models.Model):
    """Тег, используемый для классификации рецептов."""

    name = models.CharField('Название', max_length=FIELD_LENGHT, unique=True)
    slug = models.SlugField('Слаг', max_length=FIELD_LENGHT, unique=True)

    class Meta:
        """Метаданные модели Tag."""

        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        """Возвращает строковое представление тега."""
        return self.name


class Ingredient(models.Model):
    """Ингредиент с названием и единицей измерения."""

    name = models.CharField('Ингредиент', max_length=MID_FIELD_LENGHT)
    measurement_unit = models.CharField('Ед. измерения',
                                        max_length=FIELD_LENGHT)

    class Meta:
        """Метаданные модели Ingredient."""

        constraints = [
            UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_name_unit',
            )
        ]
        indexes = [
            models.Index(
                Lower('name'),
                name='idx_ingredient_name_lower',
            ),
        ]
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def clean(self):
        """
        Проверяет уникальность ингредиента с учётом регистра.
        """
        name = (self.name or '').strip()
        unit = (self.measurement_unit or '').strip()

        qs = Ingredient.objects.filter(
            name__iexact=name,
            measurement_unit__iexact=unit,
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)

        if qs.exists():
            raise ValidationError(
                'Такой ингредиент с этой единицей уже существует.'
            )

    def save(self, *args, **kwargs):
        """
        Очищает поля от пробелов перед сохранением.
        """
        if self.name:
            self.name = self.name.strip()
        if self.measurement_unit:
            self.measurement_unit = self.measurement_unit.strip()
        super().save(*args, **kwargs)

    def __str__(self):
        """Возвращает строковое представление ингредиента."""
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    """Рецепт, содержащий описание, фото, теги и ингредиенты."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField('Название', max_length=MAX_FIELD_LENGHT)
    text = models.TextField('Описание/рецепт')
    image = models.ImageField('Фото', upload_to=recipe_image_upload_to)
    cooking_time = models.PositiveIntegerField(
        'Время готовки (мин)',
        validators=[MinValueValidator(1)],
    )
    tags = models.ManyToManyField(
        'Tag',
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Теги',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        """Метаданные Recipe: индексы, сортировка, ограничения."""

        indexes = [
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['name']),
        ]
        constraints = [
            CheckConstraint(
                check=Q(cooking_time__gt=0),
                name='recipe_cooking_time_gt_0',
            )
        ]
        ordering = ('-created_at',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def get_absolute_url(self):
        """
        Возвращает URL рецепта на фронтенде.
        """
        base = getattr(settings, 'FRONTEND_BASE_URL', '/')
        return urljoin(base, f'recipes/{self.pk}')

    def __str__(self):
        """Возвращает название рецепта."""
        return self.name


class RecipeTag(models.Model):
    """Связь рецепта с тегом."""

    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='recipe_tags',
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE,
        related_name='tag_in_recipes',
        verbose_name='Тег',
    )

    class Meta:
        """Метаданные RecipeTag: уникальность и индексы."""

        constraints = [
            UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag',
            )
        ]
        indexes = [
            models.Index(fields=['recipe']),
            models.Index(fields=['tag']),
            models.Index(fields=['recipe', 'tag']),
        ]
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'

    def __str__(self):
        """Строковое представление связи рецепта и тега."""
        return f'{self.recipe} → {self.tag}'


class RecipeIngredient(models.Model):
    """Связь рецепта с ингредиентом и его количеством."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_in_recipes',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        """Метаданные RecipeIngredient: уникальность и валидация."""

        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='uniq_recipe_ingredient',
            ),
            CheckConstraint(
                check=Q(amount__gte=1),
                name='recipeingredient_amount_ge_1',
            ),
        ]
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        """Строковое представление ингредиента в рецепте."""
        return f'{self.ingredient} × {self.amount} (в {self.recipe})'
