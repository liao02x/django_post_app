from django_post.settings import abstract_geo_api_url, abstract_holidays_api_url
import requests
from requests.adapters import HTTPAdapter, Retry
import logging


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_ip_location(ip):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1,
                    status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    response = session.get(abstract_geo_api_url + "&ip_address=" + ip)
    response.raise_for_status()

    json_response = response.json()

    logging.info(f"json_response: {json_response}, {json_response.get('timezone')}")

    return {
        'country': json_response["country_code"],
        'timezone': json_response.get("timezone", dict()).get("gmt_offset", None),
        'lat': json_response["latitude"],
        'lon': json_response["longitude"],
    }


def get_holiday_info(country, year, month, day):
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1,
                    status_forcelist=[502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    response = session.get(f"{abstract_holidays_api_url}&country={country}&year={year}&month={month}&day={day}")
    
    response.raise_for_status()

    json_response = response.json()

    logging.info(f"json_response: {json_response}")

    return json_response
