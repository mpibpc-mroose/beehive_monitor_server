from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView

from DataCollector.views import (
    AmChartView,
    MeasurementTableView
)

urlpatterns = [
    url(r"favicon.ico", RedirectView.as_view(url="static/icons/favicon.ico")),
    url(r"collector/", include("DataCollector.urls")),
    url('accounts/', include('django.contrib.auth.urls')),
    url(
        regex='admin/',
        view=admin.site.urls
    ),
    url(
        regex="^tabelle/$",
        view=MeasurementTableView.as_view(),
        name="table"
    ),
    url(
        regex="^$",
        view=AmChartView.as_view(),
        name="home"
    )
]
