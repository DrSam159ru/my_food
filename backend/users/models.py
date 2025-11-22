from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q, UniqueConstraint
from django.db.models.functions import Lower

from core.const import MAN_FIELD_LENGHT, STD_FIELD_LENGHT


def avatar_upload_to(instance, filename):
    """
    Возвращает путь для загрузки аватара пользователя.
    """
    user_id = instance.id or 'temp'
    return f'avatars/{user_id}/{filename}'


class UserManager(BaseUserManager):
    """Менеджер пользователей с созданием обычных и суперпользователей."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создаёт и сохраняет пользователя с указанными email и паролем.
        """
        if not email:
            raise ValueError('Необходимо ввести e-mail')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Создаёт обычного пользователя c отключёнными правами админа.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создаёт суперпользователя с обязательными правами админа.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя, использующая e-mail как имя входа.
    """

    first_name = models.CharField('Имя', max_length=STD_FIELD_LENGHT,
                                  blank=False)
    last_name = models.CharField('Фамилия', max_length=STD_FIELD_LENGHT,
                                 blank=False)
    email = models.EmailField(
        'E-mail',
        unique=True,
        blank=False,
        max_length=MAN_FIELD_LENGHT,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to=avatar_upload_to,
        null=True,
        blank=True,
    )

    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']
    USERNAME_FIELD = 'email'

    objects = UserManager()

    class Meta:
        """Метаданные модели пользователя."""

        constraints = [
            UniqueConstraint(
                Lower('email'),
                name='unique_email_ci',
            )
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def save(self, *args, **kwargs):
        """Нормализует адрес e-mail перед сохранением."""
        if self.email:
            self.email = self.email.strip().lower()
        super().save(*args, **kwargs)

    def __str__(self):
        """Возвращает строковое представление пользователя."""
        return self.username or self.email


class Follow(models.Model):
    """
    Модель подписок: пользователь → автор. Исключает самоподписку.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follows',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Автор',
    )

    class Meta:
        """Метаданные модели Follow."""

        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author_follow',
            ),
            models.CheckConstraint(
                check=~Q(user=models.F('author')),
                name='prevent_self_follow',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'author']),
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['user_id']

    def __str__(self):
        """Возвращает строковое представление подписки."""
        return f'{self.user} → {self.author}'
