import pendulum
import logging
from statistics import mean

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models.functions import TruncDate

from DataCollector.models import (
    Scale,
    Measurement,
    MeasurementDayAggregation
)

from DataCollector.utils import FakeApixuWeather, WeatherException

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def get_available_dates():
    """
    extract available dates (except today's date) from the Measurements
    :return:
    """
    available_dates = []
    for values in Measurement.objects.annotate(date=TruncDate("timestamp")).values("date").distinct():
        if values["date"] != pendulum.today().date():
            available_dates.append(values["date"])
    return available_dates


def aggregate(measurements, field):
    field_values = list(value[field] for value in measurements.values(field))
    return {
        "avg": mean(field_values),
        "min": min(field_values),
        "max": max(field_values)
    }


def convert_integer(aggregation):
    _aggregation = {}
    for key, value in aggregation.items():
        _aggregation[key] = int(round(value, 0))
    return _aggregation


def round_aggregation(aggregation):
    _aggregation = {}
    for key, value in aggregation.items():
        _aggregation[key] = round(value, 1)
    return _aggregation


class Command(BaseCommand):
    help = 'Aggregate measurements per day into MeasurementAggregation model'
    measurements = object

    def _get_apixiu_weather(self):
        """
        get the weather accumulation for yesterday from APIXU
        :return: tuple for day-JSON, rain and icon
        """
        yesterday = pendulum.yesterday()
        json = ""
        rain = 0.0
        icon = ""
        try:
            w = FakeApixuWeather(
                api_key=settings.APIXU_API_KEY,
                location="Göttingen",
                day=yesterday.day,
                month=yesterday.month,
                year=yesterday.year
            )
            try:
                return str(w.day_weather_accumulation), w.rain, w.weather_icon
            except WeatherException:
                return "", 999, ""
        except WeatherException as error:
            logger.exception(error)
            return json, rain, icon

    def _get_weight_aggregation(self):
        return round_aggregation(
            aggregate(
                self.measurements,
                field="weight"
            )
        )

    def _get_temperature_aggregation(self):
        return convert_integer(
            aggregate(
                self.measurements,
                field="temperature"
            )
        )

    def _get_humidity_aggregation(self):
        return convert_integer(
            aggregate(
                self.measurements,
                field="humidity"
            )
        )

    def add_measurement_aggregation(self, day, scale):
        self.measurements = Measurement.objects.annotate(date=TruncDate("timestamp")).filter(date=day, scale=scale)
        weight_aggr = self._get_weight_aggregation()
        temperature_aggr = self._get_temperature_aggregation()
        humidity_aggr = self._get_humidity_aggregation()
        apixu_raw, rain, icon = self._get_apixiu_weather()
        MeasurementDayAggregation.objects.create(
            date=day,
            scale=scale,
            weight_avg=weight_aggr["avg"],
            weight_max=weight_aggr["max"],
            weight_min=weight_aggr["min"],
            temperature_avg=temperature_aggr["avg"],
            temperature_max=temperature_aggr["max"],
            temperature_min=temperature_aggr["min"],
            humidity_avg=humidity_aggr["avg"],
            humidity_max=humidity_aggr["max"],
            humidity_min=humidity_aggr["min"],
            rain=rain,
            icon=icon,
            apixiu_weather=apixu_raw
        )

    def handle(self, *args, **options):
        scales = Scale.objects.all()
        for day in get_available_dates():
            for scale in scales:
                try:
                    MeasurementDayAggregation.objects.get(date=day)
                except MeasurementDayAggregation.DoesNotExist:
                    self.add_measurement_aggregation(day, scale=scale)
