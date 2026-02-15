from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.workers.tasks import RateLimitRuleUpdater

scheduler = AsyncIOScheduler()

def start_scheduler(updater: RateLimitRuleUpdater):
    scheduler.add_job(updater.update_rules, "interval", minutes=1)
    scheduler.start()
