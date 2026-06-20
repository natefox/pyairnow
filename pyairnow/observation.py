'''Retrieve a list of Current Observations'''
from typing import Callable, Coroutine, Optional, Union


CATEGORY_NAME_TO_NUMBER = {
    'Good': 1,
    'Moderate': 2,
    'Unhealthy for Sensitive Groups': 3,
    'Unhealthy': 4,
    'Very Unhealthy': 5,
    'Hazardous': 6,
}


PARAMETER_NAME_MAP = {
    'OZONE': 'O3',
}


def _normalize_observation(raw: dict) -> dict:
    '''Transform new API response format to legacy format for compatibility.'''
    hour_raw = raw.get('hourObserved', 0)
    if isinstance(hour_raw, str):
        hour = int(hour_raw.split(':')[0])
    else:
        hour = int(hour_raw)

    cat_name = raw.get('aqiCategoryName', '')
    cat_number = CATEGORY_NAME_TO_NUMBER.get(cat_name, 0)

    param = raw.get('parameterName', '')
    param = PARAMETER_NAME_MAP.get(param, param)

    return {
        'DateObserved': raw.get('dateObserved', ''),
        'HourObserved': hour,
        'LocalTimeZone': raw.get('localTimeZone', ''),
        'ReportingArea': raw.get('reportingAreaName', ''),
        'StateCode': raw.get('stateCode', ''),
        'Latitude': raw.get('latitude'),
        'Longitude': raw.get('longitude'),
        'ParameterName': param,
        'AQI': raw.get('nowcastAQI', raw.get('aqi', -1)),
        'Category': {
            'Number': cat_number,
            'Name': cat_name,
        },
    }


class Observations:
    '''
    Class to retrieve the current air quality observations by zip code or by
    latitude and longitude.
    '''
    def __init__(self, request: Callable[..., Coroutine]) -> None:
        self._request = request

    async def zipCode(
        self,
        zipCode: str,
        *,
        distance: Optional[int] = None
    ) -> list:
        '''Request current observation for zip code'''
        params: dict = dict(zipCode=zipCode)
        if distance:
            params['distance'] = distance

        data = await self._request(
            'aq/observation/current/ziplatlong',
            params=params
        )
        return [_normalize_observation(o) for o in data]

    async def latLong(
        self,
        latitude: Optional[Union[float, str]] = None,
        longitude: Optional[Union[float, str]] = None,
        *,
        distance: Optional[int] = None,
    ) -> list:
        '''Request current observation for latitude/longitude'''
        params: dict = dict(
            latitude=str(latitude),
            longitude=str(longitude),
        )
        if distance:
            params['distance'] = distance

        data = await self._request(
            'aq/observation/current/ziplatlong',
            params=params
        )
        return [_normalize_observation(o) for o in data]
