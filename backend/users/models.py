import os

from dotenv import load_dotenv

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


load_dotenv()


STR_MAX_LENGTH = int(os.getenv('MODEL_STR_MAX_LENGTH', default=30))


class User(AbstractUser):
    """
    Модель пользователя.

    Обязательные поля:
    - username (имя пользователя);
    - email (адрес электронной почты);
    - first_name (имя);
    - last_name (фамилия);
    - password (пароль).

    Уникальные поля:
    - username (имя пользователя);
    - email (адрес электронной почты).
    """

    password = models.CharField(_('password'), max_length=150)
    email = models.EmailField(
        _('email address'),
        max_length=254,
        help_text=_('Обязательное поле. Не более 254 символов.'),
        unique=True,
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        help_text=_('Обязательное поле. Не более 150 символов.'),
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        help_text=_('Обязательное поле. Не более 150 символов.'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self) -> str:
        return self.get_username()[:STR_MAX_LENGTH]


class Follow(models.Model):
    """
    Модель подписки.

    На каждого автора можно подписаться только 1 раз.
    Нельзя подписаться на себя.
    """

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=_('Подписчик'),
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('Автор'),
    )

    class Meta:
        verbose_name = _('Подписка')
        verbose_name_plural = _('Подписки')
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_follower_following',
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='prevent_self_follow',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.follower} подписан на {self.following}'
