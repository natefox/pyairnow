'''Retrieve Air Quality Forecasts'''
from datetime import date as date_, datetime
from typing import Callable, Coroutine, Optional, Union


PARAMETER_NAME_MAP = {
    'OZONE': 'O3',
}


def _normalize_forecast(raw: dict) -> dict:
    '''Transform new API response format to legacy format for compatibility.'''
    cat_number = raw.get('categoryNumber', raw.get('Category', {}).get('Number', 0))
    cat_name = raw.get('categoryName', raw.get('Category', {}).get('Name', ''))

    param = raw.get('parameterName', raw.get('ParameterName', ''))
    param = PARAMETER_NAME_MAP.get(param, param)

    return {
        'DateIssue': raw.get('dateIssue', ''),
        'DateForecast': raw.get('dateValid', raw.get('DateForecast', '')),
        'ReportingArea': raw.get('reportingArea', raw.get('ReportingArea', '')),
        'StateCode': raw.get('stateCode', raw.get('StateCode', '')),
        'Latitude': raw.get('latitude', raw.get('Latitude')),
        'Longitude': raw.get('longitude', raw.get('Longitude')),
        'ParameterName': param,
        'AQI': raw.get('aqi', raw.get('AQI', -1)),
        'Category': {
            'Number': cat_number,
            'Name': cat_name,
        },
        'ActionDay': raw.get('actionDay', raw.get('ActionDay', False)),
        'Discussion': raw.get('discussion', raw.get('Discussion', '')),
    }


class Forecast:
    '''
    Class to retrieve the air quality forecast by zip code or by latitude and
    longitude.
    '''
    def __init__(self, request: Callable[..., Coroutine]) -> None:
        self._request = request

    async def zipCode(
        self,
        zipCode: str,
        *,
        date: Optional[Union[date_, datetime, str]] = None,
        distance: Optional[int] = None
    ) -> list:
        '''Request forecast for zip code'''
        params: dict = dict(zipCode=zipCode)
        if date and isinstance(date, str):
            y, m, d = date.split('-')
            params['date'] = date_(int(y), int(m), int(d)).isoformat()
        elif date and isinstance(date, datetime):
            params['date'] = date.date().isoformat()
        elif date and isinstance(date, date_):
            params['date'] = date.isoformat()
        if distance:
            params['distance'] = distance

        data = await self._request(
            'aq/forecast/current',
            params=params
        )
        return [_normalize_forecast(f) for f in data]

    async def latLong(
        self,
        latitude: Optional[Union[float, str]] = None,
        longitude: Optional[Union[float, str]] = None,
        *,
        date: Optional[Union[date_, datetime, str]] = None,
        distance: Optional[int] = None,
    ) -> list:
        '''Request forecast for latitude/longitude'''
        params: dict = dict(
            latitude=str(latitude),
            longitude=str(longitude),
        )
        if date and isinstance(date, str):
            y, m, d = date.split('-')
            params['date'] = date_(int(y), int(m), int(d)).isoformat()
        elif date and isinstance(date, datetime):
            params['date'] = date.date().isoformat()
        elif date and isinstance(date, date_):
            params['date'] = date.isoformat()
        if distance:
            params['distance'] = distance

        data = await self._request(
            'aq/forecast/current',
            params=params
        )
        return [_normalize_forecast(f) for f in data]
