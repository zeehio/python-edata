"""A REData API connector"""

import datetime as dt
import logging

import httpx
from dateutil import parser

from ..definitions import PricingData

_LOGGER = logging.getLogger(__name__)

REQUESTS_TIMEOUT = 15

URL_REALTIME_PRICES = (
    "https://apidatos.ree.es/es/datos/mercados/precios-mercados-tiempo-real"
    "?time_trunc=hour"
    "&geo_ids={geo_id}"
    "&start_date={start:%Y-%m-%dT%H:%M}&end_date={end:%Y-%m-%dT%H:%M}"
)


def _pricing_data_from_json(url, res) -> list[PricingData]:
    try:
        res_list = res.json()["included"][0]["attributes"]["values"]
    except IndexError:
        _LOGGER.error(
            "%s returned a malformed response: %s ",
            url,
            res.text,
        )
        return []
    return [
        PricingData(
          datetime=parser.parse(element["datetime"]).replace(tzinfo=None),
          value_eur_kWh=element["value"] / 1000,
          delta_h=1,
        )
        for element in res_list
    ]


class AsyncREDataConnector:
    """Main class for REData connector"""

    async def __init__(
        self,
    ) -> None:
        """Init method for REDataConnector"""

    async def get_realtime_prices(
        self, dt_from: dt.datetime, dt_to: dt.datetime, is_ceuta_melilla: bool = False
    ) -> list[PricingData]:
        """GET query to fetch realtime pvpc prices, historical data is limited to current month"""
        url = URL_REALTIME_PRICES.format(
            geo_id=8744 if is_ceuta_melilla else 8741,
            start=dt_from,
            end=dt_to,
        )
        async with httpx.AsyncClient() as client:
            res = await client.get(url, timeout=REQUESTS_TIMEOUT)
        if res.status_code != 200 or not res.json():
            _LOGGER.error(
                "%s returned %s with code %s",
                url,
                res.text,
                res.status_code,
            )
            return []
        return _pricing_data_from_json(url, res)


class REDataConnector:
    """Main class for REData connector"""

    def __init__(
        self,
    ) -> None:
        """Init method for REDataConnector"""

    def get_realtime_prices(
        self, dt_from: dt.datetime, dt_to: dt.datetime, is_ceuta_melilla: bool = False
    ) -> list:
        """GET query to fetch realtime pvpc prices, historical data is limited to current month"""
        url = URL_REALTIME_PRICES.format(
            geo_id=8744 if is_ceuta_melilla else 8741,
            start=dt_from,
            end=dt_to,
        )
        res = httpx.get(url, timeout=REQUESTS_TIMEOUT)
        if res.status_code != 200 or not res.json():
            _LOGGER.error(
                "%s returned %s with code %s",
                url,
                res.text,
                res.status_code,
            )
            return []
        return _pricing_data_from_json(url, res)
