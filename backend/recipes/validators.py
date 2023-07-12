from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class HexColorValidator(RegexValidator):
    """Проверка, что строка представлена в HEX-формате."""

    regex = r'^#[0-9A-Fa-f]{3,6}$'
    message = _(
        'Значение цвета должно быть корректной HEX-строкой: '
        'содержит 3 или 6 символов (кроме "#"), '
        'каждый символ является цифрой или буквой от A (a) до F(f).',
    )
    flags = 0
