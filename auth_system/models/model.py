from auth_system.models.base import BaseAbstractUser


class CustomUser(BaseAbstractUser):
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
        db_table = 'custom_users'