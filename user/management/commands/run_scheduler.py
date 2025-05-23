from apscheduler.schedulers.background import BackgroundScheduler

from user.cron import check_availblity_of_driver, delete_api_log

scheduler = BackgroundScheduler()

def run_scheduler():
    scheduler.add_job(check_availblity_of_driver, 'interval', minutes=10)
    scheduler.add_job(delete_api_log, 'cron', hour=16, minute=8)
    scheduler.start()
    print(":alarm_clock: APScheduler started.")