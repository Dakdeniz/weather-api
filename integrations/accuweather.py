from django.conf import settings
import requests
from typing import List, Optional, Any
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import humps
from weather.models import WeatherCondition, CurrentWeather, DailyForecast
from operator import itemgetter
from datetime import datetime


@dataclass_json
@dataclass
class GenericResponse:
    """Generic Response for API calls"""

    status: int = 200
    data: Optional[Any] = None
    message: Optional[dict] = None


class AccuWeatherAPI(object):

    """Client for AccuWeather API.

    AccuWeather API uses location key to retrieve current weather or forecast for a specific location.
    We have to first find location key by city and country (optional) names.

    """

    def __init__(self, api_key: str):
        """Accuweather API is initialized with required URLs to make calls.

        External API (rest countries) is used to get ISO 2 letter country codes.

        Args:
            api_key (str): Accuweather API key used in all API calls
        """
        self.apikey = api_key
        self.base_url = "http://dataservice.accuweather.com"
        self.location_url = f"{self.base_url}/locations/v1/cities/search"
        self.current_url = f"{self.base_url}/currentconditions/v1/"
        self.forecast_url = f"{self.base_url}/forecasts/v1/daily/5day/"
        self.rest_countries_url = "https://restcountries.com/v2/"

    def get_location_key_by_search(self, city: str, country: Optional[str] = None):
        """Find location key by city and country

        If multiple locations found by city/country search, first location returned
        """

        url = self.location_url

        if country:
            ccode = self.get_country_code(country=country)
            if ccode:
                url = f"{self.base_url}/locations/v1/cities/{ccode}/search"

        params = {"q": city, "apikey": self.apikey}

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()

        except Exception as e:
            return GenericResponse(
                status=e.response.status_code,
                message=e.response.json(),
            )

        else:
            if response.status_code == 200 and response.json():
                location_key = response.json()[0]["Key"]
                return GenericResponse(data=location_key)
            else:
                return GenericResponse(
                    status=404, message="No location found for the city"
                )

    def get_country_code(self, country: str):
        """Find 2 letter country code with its name

        Args:
            country (str): country name

        """
        params = {"apikey": self.apikey}

        try:
            response = requests.get(
                f"{self.rest_countries_url}name/{country}", params=params, timeout=5
            )
            response.raise_for_status()

        except Exception as e:
            return GenericResponse(
                status=e.response.status_code,
                message=e.response.json(),
            )

        else:
            if response.status_code == 200 and response.json():
                country = response.json()[0]
                country_code = country.get("alpha2Code")
                return GenericResponse(data=country_code)
            else:
                return GenericResponse(
                    status=404, message={"detail": "Can't find country code"}
                )

    def get_forecast_by_location_key(self, location_key: int):
        """Gets daily forecast (5 days) for a location defined by the location key

        Args:
            location_key (int): AccuWeather location code

        """

        params = {"apikey": self.apikey}
        try:
            response = requests.get(
                self.forecast_url + str(location_key), params=params, timeout=5
            )
            response.raise_for_status()

        except Exception as e:
            return GenericResponse(
                status=e.response.status_code,
                message=e.response.json(),
            )

        else:
            if response.status_code == 200 and response.json():

                return GenericResponse(data=response.json())
            else:
                return GenericResponse(
                    status=404, message={"detail": "Can't get forecast data"}
                )

    def get_forecast(self, *, city: str, country: Optional[str] = None):
        """Gets daily forecast (5 days) for a location defined by city and country

        Args:
            city (str): city name
            country (Optional[str], optional): Country name. Defaults to None.
        """

        response = self.get_location_key_by_search(
            city=city,
            country=country,
        )

        if response.status != 200:
            return GenericResponse(status=response.status, message=response.message)

        forecast = self.get_forecast_by_location_key(location_key=response.data)

        return GenericResponse(data=forecast.data)

    def get_current_weather_by_location_key(self, location_key: int):
        """Gets current weather condition for a location defined by the location key

        Args:
            location_key (int): AccuWeather location code

        """

        params = {"apikey": self.apikey}

        try:
            response = requests.get(
                self.current_url + str(location_key), params=params, timeout=5
            )
            response.raise_for_status()

        except Exception as e:
            return GenericResponse(
                status=e.response.status_code,
                message=e.response.json(),
            )

        else:
            if response.status_code == 200 and response.json():

                return GenericResponse(data=response.json())
            else:
                return GenericResponse(
                    status=404, message={"detail": "Can't get current weather data"}
                )

    def get_current_weather(self, *, city: str, country: Optional[str] = None):
        """Gets current weather condition for a location defined by city and country

        Args:
            city (str): city name
            country (Optional[str], optional): Country name. Defaults to None.
        """

        response = self.get_location_key_by_search(city=city, country=country)

        if response.status != 200:
            return GenericResponse(status=response.status, message=response.message)

        current = self.get_current_weather_by_location_key(location_key=response.data)

        return GenericResponse(data=current.data)

    @staticmethod
    def forecast_to_model(
        data: list,
        sort_by: Optional[str] = None,
        descending: bool = False,
    ):
        """Converts forecast data to dataclass models

        Args:
            data (list): list of daily forecasts
            sort_by (Optional[str], optional): Sort key. Defaults to None.
            descending (bool, optional): Sort direction. Defaults to ascending.
        """

        mapped = []

        for line in data:
            record = humps.decamelize(line)
            date, temperature, day, night = itemgetter(
                "date", "temperature", "day", "night"
            )(record)

            day_condition = WeatherCondition.from_dict(day)
            night_condition = WeatherCondition.from_dict(night)

            date = datetime.fromisoformat(date)
            min_temp = temperature.get("minimum").get("value")
            max_temp = temperature.get("maximum").get("value")

            model_data = DailyForecast(
                date=date,
                min_temp=min_temp,
                max_temp=max_temp,
                day_condition=day_condition,
                night_condition=night_condition,
            )

            mapped.append(model_data)

        if sort_by and sort_by in DailyForecast.__annotations__.keys():
            mapped = sorted(
                mapped, key=lambda fld: getattr(fld, sort_by), reverse=descending
            )
        return mapped

    @staticmethod
    def current_to_model(data: list):
        """Converts current weather data to dataclass models

        Args:
            data (list): list of current weather condition

        """

        if not data:
            return {}
        record = humps.decamelize(data[0])
        date = datetime.fromisoformat(record.pop("local_observation_date_time"))
        temperature = record.pop("temperature")
        temperature_c = temperature.get("metric").get("value")
        temperature_f = temperature.get("imperial").get("value")

        return CurrentWeather.from_dict(
            {
                **record,
                "temperature_c": temperature_c,
                "temperature_f": temperature_f,
                "date": date,
            }
        )


client = AccuWeatherAPI(api_key=settings.ACCUWEATHER_API_KEY)
