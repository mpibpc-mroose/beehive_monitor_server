import functools

from django.utils.html import mark_safe


class Plot(object):
    """
    represents a single plot of measurement data
    """
    # time_format = "DD.MM. HH:mm"
    time_format = "MM/DD/YYYY HH:mm"
    _py_time_string = "%d/%m/%Y %H:%M"
    colors = {
        "weight": "#fec509",
        "temperature": "#126398",
        "humidity": "#6fbd46"
    }

    def __init__(self, css_id, data):
        self.css_id = css_id
        self._data = data

    @property
    @functools.lru_cache()
    def _weights(self):
        return list(measurement.weight for measurement in self._data)

    @property
    @functools.lru_cache()
    def _temperatures(self):
        return list(measurement.temperature for measurement in self._data)

    @property
    @functools.lru_cache()
    def _humidities(self):
        return list(measurement.humidity for measurement in self._data)

    def _convert_to_list_string(self, field, is_datetime=False):
        field_values = ""
        value_template = '"{value}", '
        time_template = 'moment("{time}"), '
        for measurement in self._data:
            _value = getattr(measurement, field)
            if is_datetime is True:
                field_values += time_template.format(
                    time=_value.isoformat()
                )
            else:
                field_values += value_template.format(
                    value=str(_value)
                )

        return mark_safe("[" + field_values + "]")

    @property
    def labels(self):
        return self._convert_to_list_string("timestamp", is_datetime=True)

    @property
    def weights(self):
        return self._convert_to_list_string("weight")

    @property
    def temperatures(self):
        return self._convert_to_list_string("temperature")

    @property
    def humidities(self):
        return self._convert_to_list_string("humidity")

    @property
    def scales(self):
        return {
            "weight": {
                "min": min(self._weights),
                "max": max(self._weights)
            },
            "temperature": {
                "min": min(self._temperatures),
                "max": max(self._temperatures)
            },
            "humidity": {
                "min": int(min(self._humidities) / 10) * 10,
                "max": (int(max(self._humidities) / 10) +1 ) * 10
            }
        }
