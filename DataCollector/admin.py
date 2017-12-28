import uuid
from django.contrib.admin import (
    register,
    ModelAdmin
)

from DataCollector.models import Scale, Measurement


@register(Scale)
class ScaleAdmin(ModelAdmin):
    list_display = ["name", "token"]
    list_display_links = ["token"]
    list_editable = ["name"]

    def get_form(self, request, obj=None, **kwargs):
        form = super(ScaleAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['token'].initial = uuid.uuid4().hex
        return form


@register(Measurement)
class MeasurementAdmin(ModelAdmin):
    list_display = ["timestamp", "scale", "weight", "humidity", "temperature"]
    date_hierarchy = 'timestamp'
    date_hierarchy_drilldown = True
