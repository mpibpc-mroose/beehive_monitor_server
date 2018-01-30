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


@receiver(pre_save, sender=Measurement)
def enrich_measurement_with_open_weather_data(**kwargs):
    measurement = kwargs["instance"]
    if measurement.pk is None:
        w = Weather()
        measurement.pressure = w.pressure
