from statistics import mean

from django.core.management.base import BaseCommand, CommandError
from django.db.models.functions import TruncDate

from DataCollector.models import (
    Scale,
    Measurement,
    MeasurementDayAggregation
)


def get_available_dates():
    """
    extract available dates from the Measurements
    :return:
    """
    available_dates = []
    for values in Measurement.objects.annotate(date=TruncDate("timestamp")).values("date").distinct():
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
            humidity_min=humidity_aggr["min"]
        )

    def handle(self, *args, **options):
        scales = Scale.objects.all()
        for day in get_available_dates():
            for scale in scales:
                try:
                    MeasurementDayAggregation.objects.get(date=day)
                except MeasurementDayAggregation.DoesNotExist:
                    self.add_measurement_aggregation(day, scale=scale)
