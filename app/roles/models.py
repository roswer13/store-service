from django.db import models

# Create your models here.
class Role(models.Model):
    id = models.CharField(max_length=36, primary_key=True, editable=True)
    name = models.CharField(max_length=36, unique=True)
    image = models.CharField(max_length=255)
    route = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']
