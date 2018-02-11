import uuid
from django.contrib.admin import (
    register,
    ModelAdmin
)

from DataCollector.models import (
    Scale,
    Measurement,
    MeasurementDayAggregation
)


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


@register(MeasurementDayAggregation)
class MeasurementAdmin(ModelAdmin):
    list_display = ["date", "scale", "weight_avg", "note"]
    list_editable = ["note"]
    readonly_fields = ["apixiu_weather"]
    date_hierarchy = 'date'
    date_hierarchy_drilldown = True
