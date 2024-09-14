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


class REDataConnector:
    """Main class for REData connector"""

    def __init__(
        self,
    ) -> None:
        """Init method for REDataConnector"""

    def _process_response(self, res, url) -> list[PricingData]:
        if res.status_code != 200 or not res.json():
            _LOGGER.error(
                "%s returned %s with code %s",
                url,
                res.text,
                res.status_code,
            )
            return []
        res_json = res.json()
        try:
            res_list = res_json["included"][0]["attributes"]["values"]
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

    def get_realtime_prices(
        self, dt_from: dt.datetime, dt_to: dt.datetime, is_ceuta_melilla: bool = False
    ) -> list[PricingData]:
        """GET query to fetch realtime pvpc prices, historical data is limited to current month"""
        url = URL_REALTIME_PRICES.format(
            geo_id=8744 if is_ceuta_melilla else 8741,
            start=dt_from,
            end=dt_to,
        )
        res = httpx.get(url, timeout=REQUESTS_TIMEOUT)
        return self._process_response(res, url)
