from django.contrib import admin

# Register your models here.

from user.models import (
    User,
    FileForm,
)

admin.site.register(User)
admin.site.register(FileForm)
