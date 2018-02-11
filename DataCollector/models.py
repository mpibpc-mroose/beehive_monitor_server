import logging
import uuid

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

from DataCollector.utils import Weather

logger = logging.getLogger(__name__)


class Scale(models.Model):
    name = models.CharField(
        verbose_name="Name",
        max_length=15,
        unique=True
    )
    token = models.UUIDField(
        verbose_name="Token",
    )

    def __str__(self):
        return "Scale {name}".format(name=self.name)


@receiver(pre_save, sender=Scale)
def create_uuid(sender, instance, **kwargs):
    if not instance.token:
        instance.token = uuid.uuid4().hex
        logger.debug(
            "generated UUID for scale {name}".format(
                name=instance.name
            )
        )


class Measurement(models.Model):
    scale = models.ForeignKey(
        Scale
    )
    timestamp = models.DateTimeField(
        verbose_name="timestamp"
    )
    temperature = models.FloatField(
        verbose_name="temperature"
    )
    humidity = models.FloatField(
        verbose_name="humidity"
    )
    weight = models.FloatField(
        verbose_name="weight"
    )

    pressure = models.PositiveIntegerField(
        verbose_name="Pressure",
        default=1000
    )

    def __str__(self):
        return "Measurement: {scale}@{timestamp}".format(
            scale=self.scale.name,
            timestamp=self.timestamp.isoformat()
        )


class MeasurementDayAggregation(models.Model):
    date = models.DateField(
        verbose_name="date",
        unique=True
    )
    scale = models.ForeignKey(
        Scale
    )
    weight_min = models.FloatField(
        verbose_name="Weight (min.)"
    )
    weight_avg = models.FloatField(
        verbose_name="Weight (avg.)"
    )
    weight_max = models.FloatField(
        verbose_name="Weight (max.)"
    )

    temperature_min = models.SmallIntegerField(
        verbose_name="Temperature (min.)"
    )
    temperature_avg = models.SmallIntegerField(
        verbose_name="Temperature (avg.)"
    )
    temperature_max = models.SmallIntegerField(
        verbose_name="Temperature (max.)"
    )

    humidity_min = models.SmallIntegerField(
        verbose_name="Humidity (min.)"
    )
    humidity_avg = models.SmallIntegerField(
        verbose_name="Humidity (avg.)"
    )
    humidity_max = models.SmallIntegerField(
        verbose_name="Humidity (max.)"
    )

    rain = models.FloatField(
        verbose_name="rain sum",
        default=0.0
    )
    icon = models.URLField(
        verbose_name="weather icon",
        blank=True
    )
    apixiu_weather = models.TextField(
        verbose_name="JSON from APIXIU",
        blank=True,
        help_text="for future use"
    )

    note = models.CharField(
        verbose_name="Note",
        max_length=20,
        blank=True
    )

    def __str__(self):
        return "Measurement Aggregation for {date}".format(date=self.date.strftime("%d.%m.%Y"))


@receiver(pre_save, sender=Measurement)
def enrich_measurement_with_open_weather_data(**kwargs):
    measurement = kwargs["instance"]
    if measurement.pk is None:
        w = Weather()
        measurement.pressure = w.pressure
