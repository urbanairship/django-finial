from django.contrib import admin

from finial import models

class UserTemplateOverrideAdmin(admin.ModelAdmin):
    search_fields = ('user', 'override_name', 'override_dir')
    raw_id_fields = ('user',)
    list_display = ('user', 'override_name', 'override_dir', 'priority', )
    list_filter = ('override_name', 'override_dir', )


admin.site.register(
    models.UserTemplateOverride,
    UserTemplateOverrideAdmin
)
