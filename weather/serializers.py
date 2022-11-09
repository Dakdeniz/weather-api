from rest_framework import serializers


class WeatherConditionSerializer(serializers.Serializer):

    icon_phrase = serializers.CharField()
    has_precipitation = serializers.BooleanField()
    precipitation_type = serializers.CharField()
    precipitation_intensity = serializers.CharField()


class DailyForecastSerializer(serializers.Serializer):

    date = serializers.DateTimeField()
    min_temp = serializers.FloatField()
    max_temp = serializers.FloatField()
    day_condition = WeatherConditionSerializer()
    night_condition = WeatherConditionSerializer()


class CurrentWeatherSerializer(serializers.Serializer):

    date = serializers.DateTimeField()
    temperature_c = serializers.FloatField()
    temperature_f = serializers.FloatField()
    weather_text = serializers.CharField()
    is_day_time = serializers.BooleanField()
    has_precipitation = serializers.BooleanField()
    precipitation_type = serializers.CharField()
    precipitation_intensity = serializers.CharField()
