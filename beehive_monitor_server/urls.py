from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import (
    TemplateView,
    RedirectView
)

urlpatterns = [
    url(r"favicon.ico", RedirectView.as_view(url="static/icons/favicon.ico")),
    url(r"collector/", include("DataCollector.urls")),
    url(
        regex='admin/',
        view=admin.site.urls
    ),
    url(
        regex="^$",
        view=TemplateView.as_view(template_name="home.html"),
        name="home"
    ),
]
