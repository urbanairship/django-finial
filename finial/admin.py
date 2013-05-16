from django.contrib import admin

from finial import models

class UserTemplateOverrideAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)


admin.site.register(
    models.UserTemplateOverride,
    UserTemplateOverrideAdmin
)
