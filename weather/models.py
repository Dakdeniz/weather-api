from dataclasses import dataclass
from typing import Optional
from django.db import models
from datetime import datetime
import inspect


@dataclass
class WeatherCondition:
    """WeatherCondition dataclass used as proxy model"""

    icon_phrase: str
    has_precipitation: bool = False
    precipitation_type: Optional[str] = None
    precipitation_intensity: Optional[str] = None

    @classmethod
    def from_dict(cls, env):
        """Create WeatherCondition instance by dictionary"""
        return cls(
            **{k: v for k, v in env.items() if k in inspect.signature(cls).parameters}
        )


@dataclass
class DailyForecast:
    """DailyForecast dataclass used as proxy model"""

    date: datetime
    min_temp: float
    max_temp: float
    day_condition: WeatherCondition
    night_condition: WeatherCondition

    @classmethod
    def from_dict(cls, env):
        """Create DailyForecast instance by dictionary"""
        return cls(
            **{k: v for k, v in env.items() if k in inspect.signature(cls).parameters}
        )


@dataclass
class CurrentWeather:
    """CurrentWeather dataclass used as proxy model"""

    date: datetime
    weather_text: str
    is_day_time: bool = True
    temperature_c: float = 0
    temperature_f: float = 0
    has_precipitation: bool = False
    precipitation_type: Optional[str] = None
    precipitation_intensity: Optional[str] = None

    @classmethod
    def from_dict(cls, env):
        """Create CurrentWeather instance by dictionary"""
        return cls(
            **{k: v for k, v in env.items() if k in inspect.signature(cls).parameters}
        )
