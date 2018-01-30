from copy import deepcopy
import datetime
import json
from statistics import median
import uuid

import pytz

from django.conf import settings
from django.test import TestCase
from django.urls import reverse_lazy

from DataCollector.models import (
    Scale,
    Measurement
)


class DataCollectorTestCase(TestCase):
    def setUp(self):
        # as SQLite does otherwise not allow
        # timezone aware dates
        settings.USE_TZ = True
        self.scale = Scale.objects.create(
            name="Scale at home"
        )
        self.measurement_data = {
            "timestamp": datetime.datetime.now(pytz.timezone('Europe/Berlin')).isoformat(),
            "weight": {
                "value": [55.8, 55.7, 55.8],
                "unit": "kg"
            },

            "temperature": {
                "value": 20.3,
                "unit": "°C"
            },
            "humidity": {
                "value": 65.0,
                "unit": "%"
            }
        }

    def test_01_collection_end_point(self):
        response = self.client.post(
            path=reverse_lazy("collector:incoming"),
            data={
                "token": self.scale.token,
                "data": json.dumps(self.measurement_data)
            }
        )

        self.assertEqual(
            200,
            response.status_code
        )

        self.assertEqual(
            1,
            Measurement.objects.all().count()
        )
        result = Measurement.objects.get(timestamp=self.measurement_data["timestamp"])
        self.assertEqual(
            result.scale,
            self.scale
        )
        fields_to_test = ["humidity", "temperature"]
        for field in fields_to_test:
            with self.subTest(field):
                self.assertEqual(
                    self.measurement_data[field]['value'],
                    getattr(result, field)
                )
        with self.subTest("weight gets median"):
            self.assertEqual(
                median(self.measurement_data["weight"]['value']),
                result.weight
            )

    def test_02_wrong_scale_token(self):
        response = self.client.post(
            path=reverse_lazy("collector:incoming"),
            data={
                "token": uuid.uuid4().hex,
                "data": json.dumps(self.measurement_data)
            }
        )
        self.assertNotEqual(
            200,
            response.status_code
        )

    def test_03_no_token_posted(self):
        response = self.client.post(
            path=reverse_lazy("collector:incoming"),
            data={
                "data": json.dumps(self.measurement_data)
            }
        )
        self.assertNotEqual(
            200,
            response.status_code
        )

    def test_04_no_data_posted(self):
        response = self.client.post(
            path=reverse_lazy("collector:incoming"),
            token=self.scale.token
        )
        self.assertNotEqual(
            200,
            response.status_code
        )

    def test_05_missing_field(self):
        data = deepcopy(self.measurement_data)
        data.pop("temperature")
        response = self.client.post(
            path=reverse_lazy("collector:incoming"),
            token=self.scale.token,
            data=data
        )
        self.assertNotEqual(
            200,
            response.status_code
        )

    def test_wrong_data_structure(self):
        data = deepcopy(self.measurement_data)
        data["temperature"] = 55.8
        response = self.client.post(
            path=reverse_lazy("collector:incoming"),
            token=self.scale.token,
            data=data
        )
        self.assertNotEqual(
            200,
            response.status_code
        )


class OWMTestCase(TestCase):
    def setUp(self):
        self.scale = Scale.objects.create(
            name="Foo"
        )
    def test_01_pressure(self):
        from DataCollector.utils import Weather
        weather = Weather()
        pressure = weather.pressure
        self.assertIsInstance(
            pressure,
            int,
            "integer expected, got {0}".format(str(type(pressure)))
        )
        self.assertLessEqual(
            pressure,
            1050,
            "pressure expected to be less than 1050, got {0}".format(pressure)

        )
        self.assertGreaterEqual(
            pressure,
            950,
            "pressure expected to be greater than 950, got {0}".format(pressure)
        )

    def test_02_pressure_is_added_on_new_measurements(self):
        new_measurement = Measurement.objects.create(
            scale=self.scale,
            timestamp=datetime.datetime.now(),
            temperature=20,
            humidity=60,
            weight=50
        )
        new_measurement.save()
        self.assertNotEqual(
            1000,
            Measurement.objects.get(pk=new_measurement.pk).pressure
        )