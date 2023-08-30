__all__ = ('BaseAbstractUser',)

from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.db.models import CharField, BooleanField, DateTimeField
from auth_system.models.manager import BaseManagerUser


class BaseAbstractUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    full_name = CharField(_("full name"), max_length=150, blank=True)
    is_phone = BooleanField(_("is phone"), default=False)
    phone_or_email = CharField(_("phone or email"),
                               max_length=50,
                               unique=True,
                               error_messages={"unique": _("A user with that phone or email already exists.")})

    username = CharField(_("username"),
                         max_length=150,
                         unique=True,
                         help_text=_("Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."),
                         validators=[username_validator],
                         error_messages={"unique": _("A user with that username already exists.")},
                         )

    is_staff = BooleanField(_("staff status"),
                            default=False,
                            help_text=_("Designates whether the user can log into this admin site."))

    is_active = BooleanField(_("active"),
                             default=False,
                             help_text=_(
                                 "Designates whether this user should be treated as active. "
                                 "Unselect this instead of deleting accounts."))

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    objects = BaseManagerUser()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['phone_or_email']

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = True

