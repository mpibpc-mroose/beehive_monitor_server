import datetime
import dateutil.parser
import json
import logging
from statistics import (
    median,
    StatisticsError
)

from django.db.models import (Min, Max)
from django.db.models.functions import TruncDate

from django.http import (
    HttpResponse,
    HttpResponseBadRequest
)
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, TemplateView, ListView

from braces.views import LoginRequiredMixin
import pendulum

from DataCollector.models import (
    Scale,
    Measurement,
    MeasurementDayAggregation
)
from DataCollector.plot import Plot

logger = logging.getLogger(__name__)


class BeeHiveScaleView(LoginRequiredMixin, TemplateView):
    template_name = "scale_view.html"

    @staticmethod
    def get_latest_measurement():
        return Measurement.objects.latest("timestamp")

    @staticmethod
    def calculate_median_weight(measurements):
        weights = list(measurement.weight for measurement in measurements)
        try:
            return float(round(median(weights), 2))
        except StatisticsError:
            return float(0)

    def get_weight_delta(self):
        today_weight = self.calculate_median_weight(
            Measurement.objects.filter(
                timestamp__day=datetime.date.today().day,
                timestamp__month=datetime.date.today().month,
                timestamp__year=datetime.date.today().year,
            )
        )
        yesterday_weight = self.calculate_median_weight(
            Measurement.objects.filter(
                timestamp__day=datetime.date.today().day - 1,
                timestamp__month=datetime.date.today().month,
                timestamp__year=datetime.date.today().year,
            )
        )
        week_before_weight = self.calculate_median_weight(
            Measurement.objects.filter(
                timestamp__day=datetime.date.today().day - 7,
                timestamp__month=datetime.date.today().month,
                timestamp__year=datetime.date.today().year,
            )
        )
        month_before_weight = self.calculate_median_weight(
            Measurement.objects.filter(
                timestamp__day=datetime.date.today().day - 30,
                timestamp__month=datetime.date.today().month,
                timestamp__year=datetime.date.today().year,
            )
        )
        return {
            "day": round(today_weight - yesterday_weight, 2),
            "week": round(today_weight - week_before_weight, 2),
            "month": round(today_weight - month_before_weight, 2)
        }

    def get_context_data(self, **kwargs):
        context_data = super(BeeHiveScaleView, self).get_context_data(**kwargs)
        context_data["latest_measurement"] = self.get_latest_measurement()
        context_data["weight_delta"] = self.get_weight_delta()
        context_data["measurements_today"] = Measurement.objects.filter(
            timestamp__day=datetime.date.today().day,
            timestamp__month=datetime.date.today().month,
            timestamp__year=datetime.date.today().year,
        )
        context_data["day_plot"] = Plot(
            css_id="day_chart",
            data=Measurement.objects.filter(
                timestamp__gte=datetime.datetime.now() - datetime.timedelta(hours=120)
            )
        )
        return context_data


class AmChartView(LoginRequiredMixin, TemplateView):
    template_name = "amplot.html"

    @staticmethod
    def get_latest_measurement():
        return Measurement.objects.latest("timestamp")

    @staticmethod
    def calculate_median_weight(measurements):
        weights = list(measurement.weight for measurement in measurements)
        try:
            return float(round(median(weights), 2))
        except StatisticsError:
            return float(0)

    def get_twenty_four_hour_weight_average(self):
        return self.calculate_median_weight(
            Measurement.objects.filter(
                timestamp__gte=now() - datetime.timedelta(hours=24)
            )
        )

    def get_day_diff(self):
        """ maximum last day vs. latest measurement """
        maximum_yesterday_weight = Measurement.objects.annotate(date=TruncDate("timestamp")) \
            .filter(date=pendulum.yesterday()).aggregate(Max("weight"))
        try:
            return round(self.get_latest_measurement().weight - maximum_yesterday_weight["weight__max"], 2)
        except TypeError:
            return float(0)

    def get_intra_day_diff(self):
        """ minimum current day vs. latest measurement"""
        minimum_today_weight = Measurement.objects.annotate(date=TruncDate("timestamp")) \
            .filter(date=pendulum.today()).aggregate(Min("weight"))
        try:
            return round(self.get_latest_measurement().weight - minimum_today_weight["weight__min"], 2)
        except TypeError:
            return float(0)

    def get_weight_diff(self, days_before):
        try:
            weight_in_past = MeasurementDayAggregation.objects.get(
                date=(now() - datetime.timedelta(days=days_before)).date()
            ).weight_avg
        except MeasurementDayAggregation.DoesNotExist:
            weight_in_past = MeasurementDayAggregation.objects.first().weight_avg

        return round(
            self.get_latest_measurement().weight - weight_in_past,
            1
        )

    def get_weight_delta(self):

        return {
            "day": self.get_day_diff(),
            "intra_day": self.get_intra_day_diff(),
            "week": self.get_weight_diff(days_before=7),
            "month": self.get_weight_diff(days_before=30)
        }

    def get_context_data(self, **kwargs):
        context_data = super(AmChartView, self).get_context_data(**kwargs)
        context_data["latest_measurement"] = self.get_latest_measurement()
        context_data["measurements"] = Measurement.objects.filter(
            timestamp__gte=now() - datetime.timedelta(days=9)
        )
        context_data["weight_delta"] = self.get_weight_delta()
        return context_data


class MeasurementTableView(LoginRequiredMixin, ListView):
    model = MeasurementDayAggregation
    template_name = "table.html"
    context_object_name = "measures"

    def get_queryset(self):
        return super(MeasurementTableView, self).get_queryset().order_by("-date")


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
