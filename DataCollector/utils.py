from django.conf import settings

from pyowm import OWM


class Weather(object):
    def __init__(self, location="Göttingen,DE"):
        owm = OWM(settings.OPEN_WEATHER_MAPS_API_KEY)
        observation = owm.weather_at_place(location)
        self.weather = observation.get_weather()

    @property
    def pressure(self):
        return self.weather.get_pressure()['press']

