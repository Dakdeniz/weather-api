import pytest
from urllib.parse import urlencode


class TestWeatherEndpoints:
    def test_forecast(self, api_client):

        url = "/api/forecast/?city=Paris"

        response = api_client().get(url)
        assert response.status_code == 200
        assert len(response.data) == 5
        assert {
            "date",
            "min_temp",
            "max_temp",
            "day_condition",
            "night_condition",
        } <= response.data[0].keys()

    def test_forecast_with_empty_city(self, api_client):

        url = "/api/forecast/"
        response = api_client().get(url)
        assert response.status_code == 400

    def test_current(self, api_client):

        url = "/api/current/?city=Paris"

        response = api_client().get(url)
        assert response.status_code == 200
        assert isinstance(response.data, dict)
        assert {
            "date",
            "temperature_c",
            "temperature_f",
            "weather_text",
            "has_precipitation",
        } <= response.data.keys()
