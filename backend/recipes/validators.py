from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class HexColorValidator(RegexValidator):
    """String is correct HEX-color representation."""

    regex = r'^#[0-9A-Fa-f]{3,6}$'
    message = _(
        'The color value should be a valid HEX-color: '
        'contains 3 or 6 symbols (except for "#"), '
        'each symbol is a digit or letter from A (a) to F(f).',
    )
    flags = 0
