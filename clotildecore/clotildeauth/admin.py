from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib import admin

from . import models

# Register your models here.
class UserAdmin(DefaultUserAdmin): pass

admin.site.register(models.User,UserAdmin)
