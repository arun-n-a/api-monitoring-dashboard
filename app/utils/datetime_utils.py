from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Union

from app.core.config import settings

def convert_datetime_utc_to_timezone_str(dt: datetime, timezone: str) -> str | None:
    """
    Convert input datetime object to MM-DD-YYYY HH:MM:SS string format
    """
    try:
        return datetime.strftime(
            dt.replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo(timezone)), "%m-%d-%Y %H:%M:%S")
    except Exception as e:
        print(e)
        return


def date_object_to_date_string(dt: Union[datetime.date, datetime]) -> str | None:
    """
    Change datetime or datetime object to MM-DD-YY format
    """
    try:
        return datetime.strftime(dt, '%m-%d-%Y')
    except Exception as e:
        return


def convert_timezone_to_utc_object(dt_object: datetime, timezone: str) -> datetime:
    """
    Converts a datetime object from a specific timezone to UTC.

    Args:
        dt_object (datetime.datetime): The datetime object to convert.
                                       It should be naive (without timezone information).
        time_zone (str): The string representation of the source timezone
                                   (e.g., 'America/New_York', 'Asia/Kolkata').

    Returns:
        datetime.datetime: The datetime object converted to UTC.
    """
    try:
        return dt_object.replace(tzinfo=ZoneInfo(timezone)).astimezone(ZoneInfo('UTC'))
    except Exception as e:
        return


def response_data_date_conversion(data, date_time_columns: list, timezone: str| None = settings.TIMEZONE) -> dict:
        """Convert outresponse to  schema."""
        for dt_key  in date_time_columns:
            data[dt_key] = convert_datetime_utc_to_timezone_str(data[dt_key], timezone)
        return data