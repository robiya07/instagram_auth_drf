__all__ = ('BaseManagerUser',)

from django.apps import apps
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager
import re
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


class BaseManagerUser(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, phone_or_email, password, **extra_fields):
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )

        email_validator = EmailValidator()

        if not phone_or_email:
            raise ValueError("The given phone or email must be set")
        else:
            try:
                email_validator(phone_or_email)
                is_phone = False
            except ValidationError:
                pattern = r'^\+?[0-9]+(?:[-\s][0-9]+)*$'
                if re.match(pattern, phone_or_email):
                    is_phone = True
                else:
                    raise ValueError("The given phone or email is not valid")

        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, is_phone=is_phone, phone_or_email=phone_or_email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, phone_or_email, full_name, password, **extra_fields):
        if not full_name:
            raise ValueError("The given full name must be set")
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username=username, phone_or_email=phone_or_email,
                                 full_name=full_name,
                                 password=password,
                                 **extra_fields)

    def create_superuser(self, username, phone_or_email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username=username, password=password, phone_or_email=phone_or_email, **extra_fields)

    def with_perm(
            self, perm, is_active=True, include_superusers=True, backend=None, obj=None
    ):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    "You have multiple authentication backends configured and "
                    "therefore must provide the `backend` argument."
                )
        elif not isinstance(backend, str):
            raise TypeError(
                "backend must be a dotted import path string (got %r)." % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, "with_perm"):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()
