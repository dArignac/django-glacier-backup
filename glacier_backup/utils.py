import dateutil.parser

from django.conf import settings

from pytz import timezone


def create_local_date_from_utc_datetime_without_tzinfo(str_date):
    """
    Tries to create a localized datetime from the given string that represents a datetime of UTC timezone.

    :param str_date: the datetime string
    :type str_date: str
    :return: datetime.datetime
    """
    # however there are at least two different formats for times given back from boto:
    # 2013-05-06T19:44:22.283Z
    # or
    # 2013-05-06T19:44:22Z

    try:
        return dateutil.parser.parse(str_date).astimezone(timezone(settings.TIME_ZONE))
    except (ValueError, OverflowError):
        return None
