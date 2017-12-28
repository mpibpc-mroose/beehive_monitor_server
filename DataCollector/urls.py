from django.conf.urls import url
from DataCollector.views import DataCollectorFormView

app_name = "collector"

urlpatterns = [
    url(
        regex="$",
        view=DataCollectorFormView.as_view(),
        name="incoming"
    )
]
