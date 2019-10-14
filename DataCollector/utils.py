import logging
import requests
import time
from django.conf import settings

from pyowm import OWM

logger = logging.getLogger(__name__)


class WeatherException(Exception):
    pass


class Weather(object):
    def __init__(self, location="Kassel,DE"):
        owm = OWM(settings.OPEN_WEATHER_MAPS_API_KEY)
        observation = owm.weather_at_place(location)
        self.weather = observation.get_weather()

    @property
    def pressure(self):
        return self.weather.get_pressure()['press']


class ApixuWeather(object):
    def __init__(self, api_key, location, year, month, day):
        self.raw_weather = self._get_raw_weather(
            api_key=api_key,
            location=location,
            year=year,
            month=month,
            day=day
        )

    def _get_raw_weather(self, api_key, location, year, month, day):
        max_retry_count = 10
        count = 0
        status_code = 999
        while count < max_retry_count:
            response = requests.get(
                url="https://api.apixu.com/v1/history.json?key={api_key}&q={location}&dt={year}-{month}-{day}".format(
                    api_key=api_key,
                    location=location,
                    year=year,
                    month=month,
                    day=day
                )
            )
            status_code = response.status_code
            if status_code == 200:
                return response.json()
            else:
                logger.warning(
                    "Apixiu API request failed with status {status}, retry pending".format(status=status_code))
                time.sleep(10)

        raise ApixuWeatherException("failed with status {status}".format(status=status_code))

    @property
    def day_weather_accumulation(self):
        try:
            return self.raw_weather["forecast"]["forecastday"][0]["day"]
        except IndexError:
            raise WeatherException("No Forecast in {raw_weather}".format(raw_weather=self.raw_weather))

    @property
    def rain(self):
        return self.day_weather_accumulation["totalprecip_mm"]

    @property
    def weather_icon(self):
        return self.day_weather_accumulation["condition"]["icon"]


class FakeApixuWeather(ApixuWeather):
    def day_weather_accumulation(self):
        return {
            "totalprecip_mm": -1.0,
            "condition": {
                "icon": "https://via.placeholder.com/100"
            }
        }


if __name__ == '__main__':
    w = ApixuWeather(
        api_key="0efd0031822041e7a45113647181102",
        location="Kassel",
        year=2018,
        month=2,
        day=11
    )
