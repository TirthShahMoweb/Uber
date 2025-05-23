import logging
from datetime import datetime

from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import timedelta

cron_logger = logging.getLogger("cron_logger")


def delete_api_log():
    from drf_api_logger.models import APILogsModel

    fifteen_days_ago = timezone.now() - timedelta(days=15)
    api_logs = APILogsModel.objects.filter(added_on__lt=fifteen_days_ago)
    count = api_logs.count()
    api_logs.delete()
    print(f"{count} API log(s) deleted.")
    cron_logger.info(f"{count} API log(s) deleted.")


def check_availblity_of_driver():

    from django.utils import timezone

    from user.models import DriverDetail

    drivers = DriverDetail.objects.filter(~Q(in_use=None))
    ten_minutes_ago = timezone.now() - timedelta(minutes=10)
    updated_count = 0
    for driver in drivers:
        if driver.last_online_at < ten_minutes_ago:
            driver.is_online = False
            driver.save()
            updated_count += 1

    cron_logger.info(f"{updated_count} driver(s) marked offline.")
