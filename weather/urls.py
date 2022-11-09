from django.urls import path, include
from rest_framework import routers
from weather.views import WeatherForecastViewSet, WeatherCurrentViewSet


router = routers.DefaultRouter()
router.register("forecast", WeatherForecastViewSet, basename="forecast")
router.register("current", WeatherCurrentViewSet, basename="current")


urlpatterns = [
    path("", include(router.urls)),
]
