from django.contrib import admin
from accounts import models
# Register your models here.
admin.site.register(models.Conference)
admin.site.register(models.Chair)
admin.site.register(models.Author)
admin.site.register(models.Reviewer)
admin.site.register(models.User)
admin.site.register(models.Paper)
admin.site.register(models.Submits)
admin.site.register(models.Assigns)
admin.site.register(models.Reviews)
