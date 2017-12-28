import dateutil.parser
import json
import logging
from statistics import median

from django.http import (
    HttpResponse,
    HttpResponseBadRequest
)
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from DataCollector.models import Measurement, Scale

logger = logging.getLogger(__name__)


class DataCollectorFormView(View):
    http_method_names = ["post"]

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(DataCollectorFormView, self).dispatch(request, *args, **kwargs)

    def get_scale(self, token):
        try:
            return Scale.objects.get(token=token)
        except Scale.DoesNotExist:
            return False

    @staticmethod
    def extract_measurement_model_kwargs(data):
        data = json.loads(data)
        try:
            return {
                "scale": None,
                "timestamp": dateutil.parser.parse(data["timestamp"]),
                "humidity": float(data['humidity']['value']),
                "temperature": float(data['temperature']['value']),
                "weight": float(median(data['weight']['value']))
            }
        except KeyError:
            return False

    def post(self, request, *args, **kwargs):
        try:
            token = request.POST['token']
        except KeyError:
            logging.warning("no 'token' in {request}".format(
                request=request
            ))
            return HttpResponseBadRequest()

        scale = self.get_scale(token)
        if scale is False:
            logger.warning("no scale could be found for {request}".format(
                request=request
            ))
            return HttpResponseBadRequest()

        try:
            data = request.POST['data']
        except KeyError:
            logging.warning("no 'data' in {request}".format(
                request=request
            ))
            return HttpResponseBadRequest("no data posted")

        measurement_kwargs = self.extract_measurement_model_kwargs(data)
        if data is False:
            logger.warning("wrong data structure in {request}".format(
                request=request
            ))

        measurement_kwargs["scale"] = scale
        measurement = Measurement.objects.create(**measurement_kwargs)

        return HttpResponse(
            "SUCCESS: pk is {pk}".format(
                pk=measurement.pk
            ),
            status=200
        )
