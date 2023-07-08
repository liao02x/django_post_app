from datetime import timedelta, timezone
from .utils import get_ip_location, get_holiday_info
from .models import User
import logging


def enrich_user_location(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return
    
    if (not user or not user.signup_ip):
        return

    ip = user.signup_ip
    if (not ip):
        return

    location = get_ip_location(ip)

    if (not location or not location['lat'] or not location['lon']):
        return

    if (not user.signup_country):
        user.signup_country = location['country']
    if (not user.signup_lat):
        user.signup_lat = location['lat']
    if (not user.signup_lon):
        user.signup_lon = location['lon']
    if (not user.signup_timezone):
        user.signup_timezone = location['timezone']

    logging.info(f"Saving user {user}, location {location}")

    user.save()

    enrich_user_holiday_info(email)

def enrich_user_holiday_info(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return
    
    if (not user or not user.signup_country or not user.date_joined):
        return

    country = user.signup_country
    date = user.date_joined
    if (user.signup_timezone):
        date = date.astimezone(timezone(timedelta(hours=user.signup_timezone)))

    year = date.year
    month = date.month
    day = date.day

    holiday_info = get_holiday_info(country, year, month, day)

    if (not holiday_info):
        return

    logging.info(f"holiday_info {holiday_info}")

    user.signup_holiday_info = holiday_info

    user.save()
