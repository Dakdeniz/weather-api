import pytest
from integrations.accuweather import client as aw_client, GenericResponse


@pytest.mark.parametrize(
    "country, code",
    [
        ("Germany", "DE"),
        ("Turkey", "TR"),
    ],
)
def test_retrieve_county_code(country, code):
    response = aw_client.get_country_code(country=country)

    assert isinstance(response, GenericResponse)
    assert response.status == 200
    assert response.data == code


@pytest.mark.parametrize(
    "city, status",
    [
        ("Paris", 200),
        ("AxAzAy", 404),
    ],
)
def test_get_location_key(city, status):
    response = aw_client.get_location_key_by_search(city=city)

    assert isinstance(response, GenericResponse)
    assert response.status == status


def test_get_forecast_by_city():
    response = aw_client.get_forecast(city="Hamburg")
    assert isinstance(response, GenericResponse)
    assert response.status == 200

    assert "DailyForecasts" in response.data
    assert len(response.data["DailyForecasts"]) == 5


def test_get_current_by_city():
    response = aw_client.get_current_weather(city="Hamburg")
    assert isinstance(response, GenericResponse)
    assert response.status == 200

    assert len(response.data) == 1
