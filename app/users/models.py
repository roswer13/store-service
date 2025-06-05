from django.db import models

# Create your models here.
class UserHasRoles(models.Model):
    id_user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        db_column='id_user',
        related_name='user_roles',
        help_text='User associated with the role'
    )
    id_role = models.ForeignKey(
        'roles.Role',
        on_delete=models.CASCADE,
        db_column='id_role',
        related_name='role_users',
        help_text='Role associated with the user'
    )

    class Meta:
        db_table = 'users_has_roles'
        verbose_name = 'User Role Association'
        verbose_name_plural = 'User Role Associations'
        unique_together = ('id_user', 'id_role')
        ordering = ['id_user', 'id_role']


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    image = models.CharField(max_length=255, blank=False, null=True)
    password = models.CharField(max_length=255)
    notification_token = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    roles = models.ManyToManyField(
        'roles.Role',
        related_name='users',
        through='users.UserHasRoles',
        help_text='Roles assigned to the user'
    )

    def __str__(self):
        return f"{self.name} {self.lastname} <{self.email}>"

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
