import re
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class ASCIIUsernameValidator(validators.RegexValidator):
    """
    Valide les usernames pour ne contenir que des lettres ASCII, chiffres et certains caractères.
    """
    regex = r"^[a-zA-Z0-9@.+-_]+$"
    message = _(
        "Enter a valid username. This value may contain only English letters, "
        "numbers, and @/./+/-/_ characters."
    )
    flags = re.ASCII
