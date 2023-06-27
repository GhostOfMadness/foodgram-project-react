import os

from dotenv import load_dotenv

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


load_dotenv()


STR_MAX_LENGTH = int(os.getenv('MODEL_STR_MAX_LENGTH', default=30))


class User(AbstractUser):
    """The custom User model."""

    password = models.CharField(_('password'), max_length=150)
    email = models.EmailField(_('email address'), max_length=254)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta(AbstractUser.Meta):
        indexes = [
            models.Index(fields=['email'], name='email_idx'),
        ]

    def __str__(self) -> str:
        return self.get_username()[:STR_MAX_LENGTH]

    @property
    def is_admin(self):
        """Return True if the user is a staff member (admin)."""
        return self.is_staff


class Follow(models.Model):
    """The subscription model."""

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name=_('follower'),
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name=_('following'),
    )

    class Meta:
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
