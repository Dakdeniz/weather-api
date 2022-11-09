from typing import Optional
from django.shortcuts import render
from django.utils.decorators import method_decorator
from datetime import datetime, date

# Create your views here.
from rest_framework import renderers, generics, filters
from rest_framework import views, viewsets
from rest_framework.response import Response

from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

from weather.serializers import DailyForecastSerializer, CurrentWeatherSerializer
from integrations.accuweather import AccuWeatherAPI, client

import humps


class WeatherCurrentViewSet(viewsets.ViewSet):
    """Viewset for current weather condition

    If no city provided, raises validation error.
    """

    serializer_class = DailyForecastSerializer

    def list(self, request):

        city = request.query_params.get("city")
        country = request.query_params.get("country")
        if not city:
            raise ValidationError("No city defined")

        response = client.get_current_weather(city=city, country=country)
        if response.status == 200:
            result = AccuWeatherAPI.current_to_model(data=response.data)

        else:
            raise ValidationError(response.message)

        result_data = CurrentWeatherSerializer(result or {}, many=False).data

        return Response(result_data, status=200)


class WeatherForecastViewSet(viewsets.ViewSet):
    """Viewset for daily forecasts

    If no city provided, raises validation error.
    Results can be sorted by sort_by query parameter.
    Default sorting is ascending, to sort descending descending=true should be added as query parameter
    """

    serializer_class = DailyForecastSerializer

    def list(self, request):

        city = request.query_params.get("city")
        country = request.query_params.get("country")
        sort_by = request.query_params.get("sort_by")
        descending = request.query_params.get("descending")

        results = []
        if not city:
            raise ValidationError("No city defined")

        response = client.get_forecast(city=city, country=country)
        if response.status == 200:
            results = AccuWeatherAPI.forecast_to_model(
                data=response.data["DailyForecasts"],
                sort_by=sort_by,
                descending=descending,
            )
        else:
            raise ValidationError(response.message)

        result_data = DailyForecastSerializer(results, many=True).data

        return Response(result_data, status=200)

    @method_decorator(cache_page(60 * 60 * 1))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
