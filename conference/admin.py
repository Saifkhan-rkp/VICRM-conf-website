from django.contrib import admin
from conference import models


# Register your models here.
admin.site.register(models.Site_Settings)
admin.site.register(models.Speakers)
admin.site.register(models.Patrons)
admin.site.register(models.Sponcer)
admin.site.register(models.Tickets)
admin.site.register(models.About_Conference)
admin.site.register(models.Instruction_For_Author)
# admin.site.register(models.Profile)

